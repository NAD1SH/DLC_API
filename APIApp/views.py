from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import *
import jwt
from APIApp.models import TokenAuth
from pytz import UTC
from datetime import datetime, timezone
from django.utils import timezone

current_datetime = timezone.now()
# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        Username = request.data['username']
        Password = request.data['password']

        user = CustomUser.objects.filter(username=Username).first()

        if user is None:
            raise AuthenticationFailed('User Not Found')

        if not user.check_password(Password):
            raise AuthenticationFailed('InCorrect Password')

        payload = {
            "id": user.id,
            "name": user.name,
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret',
                           algorithm='HS256').decode('utf-8')

        TokenAuth.objects.create(user=user, token=token)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            "jwt": token
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = CustomUser.objects.filter(id=playload["id"]).first()

        serializer = CustomUserSerializer(user)

        return Response(serializer.data)


class LiveSessionView(APIView):
    def get(self, request):
        status = request.query_params.get('status', None)
        LiveSession.objects.filter(start_time__lte=current_datetime,
                                   end_time__gt=current_datetime, is_status="upcoming").update(is_status="ongoing")
        LiveSession.objects.filter(
            end_time__lte=current_datetime, is_status="ongoing").update(is_status="completed")
        if status == 'upcoming':
            sessions = LiveSession.objects.filter(is_status="upcoming")
        elif status == 'ongoing':
            sessions = LiveSession.objects.filter(is_status="ongoing")
        elif status == 'completed':
            sessions = LiveSession.objects.filter(is_status="completed")
        else:
            return Response({"error": "Invalid or missing 'status' parameter"}, status=400)

        serializer = LiveSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class AddLiveSessionView(APIView):
    def post(self, request):
        serializer = LiveSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {
            "message": "success"    
        }
        return response


class AddProfileView(APIView):
    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = Profile.objects.filter(user=playload["id"]).first()
        serializer = ProfileSerializer(user)

        return Response(serializer.data)


class EditProfileView(APIView):
    def put(self, request, id):
        profile = Profile.objects.get(pk=id)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error": "Can't Update Profile"}, status=400)


class AddExamView(APIView):
    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamUnattendedList(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        
        ExamStatus.objects.filter(exam__end_date__lte = current_datetime).update(is_status="completed")
        user = CustomUser.objects.get(id=playload["id"])
        exams = Exam.objects.all()
        examStatus = ExamStatus.objects.filter(
            user=user, is_status="unattended")

        for exam in exams:
            ExamStatus.objects.get_or_create(user=user, exam=exam, defaults={
                                             "is_status": "unattended"})

        serializer = ExamStatusSerializer(examStatus, many=True)
        return Response(serializer.data)


class ExamCompletedList(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        ExamStatus.objects.filter(
            exam__end_date__lte = current_datetime).update(is_status="completed")   
        user = CustomUser.objects.get(id=playload["id"])
        examStatus = ExamStatus.objects.filter(
            user=user, is_status="completed")

        serializer = ExamStatusSerializer(examStatus, many=True)
        return Response(serializer.data)


class AttemptQuestionView(APIView):
    def get(self, request, id):
        exam = Exam.objects.get(pk = id)
        serializer = ExamSerializer(exam)
        return Response(serializer.data)


class AddExamQuestionsView(APIView):
    def post(self, request):
        serializer = ExamQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamQuestionView(APIView):
    def get(self, request, id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = CustomUser.objects.get(id=playload["id"])

        questions = Questions.objects.filter(exam=id)

        ExamStatus.objects.filter(
            user=user, exam=id).update(is_status="completed")
        data = []

        for question in questions:
            choices = question.choices.all()
            data.append({
                'id': question.id,
                'exam': id,
                'question': question.question,
                'choices': QuestionChoiceSerializer(choices, many=True).data
            })
        return Response(data)
    

class CheckCorrectAnswerView(APIView):
    def post(self, request, id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')   

        user = CustomUser.objects.get(id=playload["id"])
        que_id = QuestionChoice.objects.filter(pk = id).first()       
        question = Questions.objects.get(pk=que_id.question.id)
        choices = question.choices.get(pk=id)
        exam = Exam.objects.get(pk=question.exam.id)

        date_time = timezone.now()

        serializer = SubmitQuestionSerializer(data = {
            "user" : user.id,
            "exam" : exam.id,
            "question" : question.id,
            "answer" : choices.id
        })
        
        if SubmitQuestion.objects.filter(user = user.id, question = question.id).exists():
            return Response("Answer Already Submited", status=status.HTTP_208_ALREADY_REPORTED)
        else:
           if date_time >= exam.start_date and date_time  <= exam.end_date:
                if serializer.is_valid():
                    serializer.save()
                    return Response("Answer Submitted", status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           else:
               return Response("Exam Time Has Been Completed", status=status.HTTP_406_NOT_ACCEPTABLE)
        

class ShowResultView(APIView):
    def get(self, request, id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = CustomUser.objects.get(id=playload["id"])
        submit_que = SubmitQuestion.objects.filter(user = user, exam = id)
        question = Questions.objects.filter(exam  = id).count()
        exam = Exam.objects.get(pk = id)
        serializer = ExamSerializer(exam).data

        total_mark = 0
        correct_answer = 0
        wrong_answer = 0

        for i in submit_que:
            if i.answer.is_correct:
                total_mark += exam.mark_per_question
                correct_answer += 1
            else:
                total_mark -= exam.negative_mark
                wrong_answer += 1

        unattented_answer = question - (correct_answer + wrong_answer)

        response = Response()
        response.data = {
            "exam" : serializer,
            "total_question": question,
            "correct_answer" : correct_answer,
            "wrong_answer" : wrong_answer,
            "unattented_answer" : unattented_answer,
            "total_mark": total_mark,
        }

        return response