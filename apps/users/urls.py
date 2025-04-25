from django.urls import path
from .views import (MyTokenObtainPairView, MyTokenRefreshView, index)

app_name = 'users'

urlpatterns = [
    path('', index, name='home'),
    path('login', MyTokenObtainPairView.as_view()),
    path('refresh', MyTokenRefreshView.as_view(), name='token_refresh')

]
