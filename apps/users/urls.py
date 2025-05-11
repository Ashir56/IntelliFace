from django.urls import path
from .views import (MyTokenObtainPairView, MyTokenRefreshView, index, teacher_api, teacher_by_id_api)

app_name = 'users'

urlpatterns = [
    path('', index, name='home'),
    path('login', MyTokenObtainPairView.as_view()),
    path('refresh', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('teacher', teacher_api, name='teacher api'),
    path('teacher/<str:teacher_id>', teacher_by_id_api, name='teacher by id api')

]
