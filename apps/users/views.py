from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .helpers import send_email_confirm_account
from .serializers import MyTokenRefreshSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, Teacher, Student
from apps.core.paginations import paginated_queryset_response

# Create your views here.

from django.shortcuts import render


def index(request):
    return render(request, 'users/index.html')


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


@api_view(['POST', 'GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def user_api(request):
    if request.method == 'POST':
        data = request.data
        user = User.objects.create(**data)
        password = User.objects.make_random_password()
        user.set_password(password)
        validate_password(password)
        user.save()

        return Response({'msg': 'User created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        users = User.objects.all().order_by('created_at')
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'avatar': user.avatar if user.avatar else None,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            })
        return paginated_queryset_response(data, request)


@api_view(['PATCH', 'GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def user_by_id_api(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'PATCH':
        data = request.data
        for field_name, field_value in data.items():
            if hasattr(User, field_name):
                setattr(user, field_name, field_value)

        user.save()
        return Response({'msg': 'User updated successfully'}, status=status.HTTP_200_OK)

    if request.method == 'GET':
        data = {
            'id': user.id,
            'avatar': user.avatar if user.avatar else None,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        user.delete()
        return Response({'msg': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def teacher_api(request):
    if request.method == 'POST':
        data = request.data.dict()
        data['joining_date'] = datetime.strptime(data['joining_date'], "%Y-%m-%d").date()
        data['date_of_birth'] = datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date()
        data['is_teacher'] = True
        teacher = Teacher.objects.create(**data)
        password = Teacher.objects.make_random_password()
        teacher.set_password(password)
        validate_password(password)
        teacher.save()

        send_email_confirm_account(teacher, 'TEACHER')

        return Response({'msg': 'Teacher created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        teachers = Teacher.objects.all().order_by('created_at')
        data = []
        for teacher in teachers:
            data.append({
                'id': teacher.id,
                # 'avatar': teacher.avatar if teacher.avatar else '',
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'email': teacher.email,
                'phone_number': teacher.phone_number,
                'joining_date': teacher.joining_date,
                'date_of_birth': teacher.date_of_birth
            })
        return paginated_queryset_response(data, request)


@api_view(['PATCH', 'GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def teacher_by_id_api(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'PATCH':
        data = request.data

        for field_name, field_value in data.items():
            if hasattr(Teacher, field_name):
                setattr(teacher, field_name, field_value)

        teacher.save()
        return Response({'msg': 'User updated successfully'}, status=status.HTTP_200_OK)

    if request.method == 'GET':
        data = {
            'id': teacher.id,
            # 'avatar': teacher.avatar if teacher.avatar else '',
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'email': teacher.email,
            'phone_number': teacher.phone_number,
            'joining_date': teacher.joining_date,
            'date_of_birth': teacher.date_of_birth
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        teacher.delete()
        return Response({'msg': 'Teacher deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
