from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import Teacher, Student

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        print('Hello')
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['email'] = user.email
        token['is_active'] = user.is_active
        token['first_name'] = user.first_name
        token['is_teacher'] = user.is_teacher
        token['is_student'] = user.is_student
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number

        return token

    # def validate(self, attrs):
    #     email = attrs.get("email")
    #     password = attrs.get("password")
    #
    #     try:
    #         user = User.objects.get(email=email)
    #     except User.DoesNotExist:
    #         raise serializers.ValidationError("Invalid credentials or inactive account.")
    #
    #     print (user.is_active)
    #
    #     if not user.is_active:
    #         raise serializers.ValidationError("User account is inactive.")
    #
    #     if not user.check_password(password):
    #         raise serializers.ValidationError("Invalid credentials or inactive account.")
    #
    #         # At this point, the user is valid and password matches
    #     refresh = MyTokenObtainPairSerializer.get_token(user)
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }

class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        try:
            new_refresh = RefreshToken()
            new_refresh.set_jti()
            new_refresh.set_exp()
            new_refresh.set_iat()
            new_refresh.payload['user_id'] = refresh.payload['user_id']

            user_id = refresh.payload['user_id']
            user = User.objects.get(id=user_id)
        except TokenError:
            raise InvalidToken('Token is invalid or expired')
        except User.DoesNotExist:
            raise InvalidToken('User not found')

        new_access_token = new_refresh.access_token
        new_access_token['username'] = user.username
        new_access_token['is_superuser'] = user.is_superuser
        new_access_token['is_staff'] = user.is_staff
        new_access_token['email'] = user.email
        new_access_token['is_active'] = user.is_active
        new_access_token['first_name'] = user.first_name
        new_access_token['is_teacher'] = user.is_teacher
        new_access_token['is_student'] = user.is_student
        new_access_token['last_name'] = user.last_name
        new_access_token['phone_number'] = user.phone_number

        data = {
            'access': str(new_access_token),
            'refresh': str(new_refresh)
        }

        return data




class TeacherSerializer(serializers.ModelSerializer):
    joining_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    date_of_birth = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        exclude = ['groups', 'user_permissions']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Teacher(**validated_data)
        validate_password(password)
        user.set_password(password)
        user.save()
        return user


class StudentSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        exclude = ['groups', 'user_permissions']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Student(**validated_data)
        validate_password(password)
        user.set_password(password)
        user.save()
        return user