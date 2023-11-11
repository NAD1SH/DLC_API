from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    REQUIRED_FIELDS = []


class TokenAuth(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)

    def __str__(self):
        return self.user.name


class LiveSession(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()
    url = models.URLField()
    tutor = models.CharField(max_length=255)
    batch = models.CharField(max_length=100)
    is_status = models.CharField(max_length=100, default="upcoming")

    def __str__(self):
        return self.title
    

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    school = models.CharField(max_length=100)
    contact = models.IntegerField()
    address = models.TextField()


class Exam(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    mark_per_question = models.IntegerField()
    negative_mark = models.IntegerField()
    exam_duration = models.CharField(max_length=100)
    out_off = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class ExamStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    is_status = models.CharField(max_length=10, default='unattended')

    def __str__(self):
        return self.exam.title

    class Meta:
        verbose_name_plural = 'Exam Status'


class Questions(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.TextField()   

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = 'Questions'


class QuestionChoice(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return self.text


class Result(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_mark = models.IntegerField()

    def __str__(self):
        return self.user


class SubmitQuestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete = models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE)

    def __str__(self):
        return self.question.question