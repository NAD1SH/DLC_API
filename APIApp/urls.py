from django.urls import path
from .import views

urlpatterns = [
    path('Register/', views.RegisterView.as_view(), name='register-page'),
    path('Login/', views.LoginView.as_view(), name='login_page'),
    path('User/', views.UserView.as_view(), name='user-page'),
    path('Logout/', views.LogoutView.as_view(), name='logout'),
    path('user_list/', views.UserListView.as_view(), name='userList'),

    path('sessions/', views.LiveSessionView.as_view(), name='LiveSession'),   
    path('add_session/', views.AddLiveSessionView.as_view(), name='addSession'),

    path('add_profile/', views.AddProfileView.as_view(), name='addProfile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('update_profile/<int:id>/', views.EditProfileView.as_view(), name='editProfile'),

    path('add_exam/', views.AddExamView.as_view(), name='addExam'),

    path('unattended_list/', views.ExamUnattendedList.as_view(), name='unattendedList'),
    path('completed_list/', views.ExamCompletedList.as_view(), name='completedList'),
    path('attempt_question/<int:id>/', views.AttemptQuestionView.as_view(), name='attemptQuestion'),

    path('add_questions/', views.AddExamQuestionsView.as_view(), name='addQuestion'),
    path('exam_questions/<int:id>/', views.ExamQuestionView.as_view(), name='examQuestion'),

    path('check_question/<int:id>/', views.CheckCorrectAnswerView.as_view(), name='checkQuestion')
]
