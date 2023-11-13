from django.contrib import admin
from APIApp.models import *

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(TokenAuth)
admin.site.register(LiveSession)
admin.site.register(Profile)
admin.site.register(Exam)
admin.site.register(ExamStatus)
admin.site.register(Questions)
admin.site.register(QuestionChoice)
admin.site.register(SubmitQuestion)