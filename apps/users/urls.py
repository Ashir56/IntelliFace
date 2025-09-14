from django.urls import path
from .views import (MyTokenObtainPairView, MyTokenRefreshView, index, teacher_api, teacher_by_id_api, reset_password_confirm_link, student_api, student_by_id_api, class_api, class_by_id_api)

app_name = 'users'

urlpatterns = [
    path('', index, name='home'),
    path('login', MyTokenObtainPairView.as_view()),
    path('refresh', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('teacher', teacher_api, name='teacher api'),
    path('student', student_api, name='student api'),
    path('class', class_api, name='class api'),
    path('teacher/<str:teacher_id>', teacher_by_id_api, name='teacher by id api'),
    path('student/<str:student_id>', student_by_id_api, name='teacher by id api'),
    path('class/<str:class_id>', class_by_id_api, name='teacher by id api'),
    path('reset-password-confirm', reset_password_confirm_link, name='reset_password_confirm_link')
]
