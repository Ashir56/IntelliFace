from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import get_template


from apps.users.models import User


def get_send_email_token(email):
    try:
        user = None
        while True:
            try:
                user = User.objects.get(email=email)
                break
            except User.DoesNotExist:
                continue
        if user:
            refresh = RefreshToken.for_user(user)
            response_token = {'refresh': refresh,
                              'access': str(refresh.access_token),
                              'user': user}
            return response_token
        else:
            raise Exception
    except Exception as ex:
        raise (ValidationError({'email': [ex]}))


def send_email_confirm_account(user, type_new_acc):
    from_email = settings.CONTACT_EMAIL
    to = user.email
    token = get_send_email_token(to)['access']
    html_content = None
    subject = None
    if type_new_acc == 'TEACHER':
        subject = 'Welcome to the IntelliFace!'
        html_template = get_template('users/welcome_new_teacher.html')
        context = {
            'full_name_receiver': user.first_name + ' ' + user.last_name,
            'create_password_link': settings.TEACHER_URL +
                                    '/teacher-setup?user_type=teacher&token={}'.format(token)
        }
        html_content = html_template.render(context)

    msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=[to])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception as ex:
        print(ex)