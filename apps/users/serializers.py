from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        # token['id'] = str(user.id)
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['email'] = user.email
        # token['is_first_login'] = user.is_first_login
        # token['avatar'] = user.avatar.url if user.avatar else ''
        token['is_active'] = user.is_active
        token['first_name'] = user.first_name
        token['is_teacher'] = user.is_teacher
        token['is_student'] = user.is_student
        # token['middle_name'] = user.middle_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number

        return token


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        try:
            # Manually rotate the refresh token
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

        # Create new access token
        new_access_token = new_refresh.access_token

        new_access_token['username'] = user.username
        # token['id'] = str(user.id)
        new_access_token['is_superuser'] = user.is_superuser
        new_access_token['is_staff'] = user.is_staff
        new_access_token['email'] = user.email
        # token['is_first_login'] = user.is_first_login
        # token['avatar'] = user.avatar.url if user.avatar else ''
        new_access_token['is_active'] = user.is_active
        new_access_token['first_name'] = user.first_name
        new_access_token['is_teacher'] = user.is_teacher
        new_access_token['is_student'] = user.is_student
        # token['middle_name'] = user.middle_name
        new_access_token['last_name'] = user.last_name
        new_access_token['phone_number'] = user.phone_number

        data = {
            'access': str(new_access_token),
            'refresh': str(new_refresh)
        }

        return data
