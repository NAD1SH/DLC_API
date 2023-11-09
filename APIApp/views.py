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


class UserListView(APIView):
    def get(self, request):
        user_list = CustomUser.objects.all()
        serializer = CustomUserSerializer(user_list, many=True)
        return Response(serializer.data)


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
        
        ExamStatus.objects.filter(exam__end_date__lt=current_datetime).update(is_status="completed")
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
            exam__end_date__lt=current_datetime).update(is_status="completed")
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
        questions = Questions.objects.filter(exam=id)
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
    def post(self, request, id1, id2):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            playload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')   

        user = CustomUser.objects.get(id=playload["id"])
        question = Questions.objects.get(pk = id1)
        choices = question.choices.get(pk = id2)
        exam = Exam.objects.get(pk = question.exam.id)

        serializer = SubmitQuestionSerializer(data=request.data)
        
        # serializer.save()
        # return Response("Answer Submited")   

        if serializer.is_valid():
            # serializer.save()
            return Response("Answer Submitted", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # data = []
        
        # data.append({
        #     'question' : question.question,
        #     'choices': QuestionChoiceSerializer(choices).data
        # })
        # return Response(data)

class ShowResultView(APIView):
    def get(self, request):
        pass 