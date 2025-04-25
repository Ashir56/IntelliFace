from django.urls import path
from .views import (MyTokenObtainPairView, MyTokenRefreshView)

app_name = 'users'

urlpatterns = [
    path('login', MyTokenObtainPairView.as_view()),
    path('refresh', MyTokenRefreshView.as_view(), name='token_refresh')

]
