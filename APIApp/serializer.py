from rest_framework import serializers
from .models import *


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'username' , 'email', 'password']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    

class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = ['id', 'title', 'start_time', 'end_time', 'description', 'url', 'tutor', 'batch', 'is_status']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'school', 'contact', 'address']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title','start_date', 'end_date', 'mark_per_question', 'negative_mark', 'exam_duration']


class ExamStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamStatus
        fields = ['id', 'user', 'exam', 'is_status']


class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['id', 'exam', 'question']


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ['id', 'text', 'is_correct']


class SubmitQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitQuestion
        fields = '__all__'