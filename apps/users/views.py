from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from ..core.embedding import student_picture_embedding

from .helpers import send_email_confirm_account
from .serializers import CourseSerializer, MyTokenRefreshSerializer, MyTokenObtainPairSerializer, StudentImageSerializer, TeacherSerializer, StudentSerializer, \
    ClassSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Course, StudentImage, User, Teacher, Student, Class
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
        data = request.data.copy()
        if User.objects.filter(email=data['email']).count() > 0:
            raise ValidationError({'msg': "Email already exist"})

        data['joining_date'] = datetime.strptime(data['joining_date'], "%Y-%m-%d").date()
        if 'date_of_birth' in data:
            data['date_of_birth'] = datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date()
        data['is_teacher'] = True
        data['is_active'] = True
        password = Teacher.objects.make_random_password()
        data['password'] = password

        serializer = TeacherSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # teacher = Teacher.objects.create(**data)
        # password = Teacher.objects.make_random_password()
        # validate_password(password)
        # serializer.set_password(password)
        #
        # serializer.save()

        # send_email_confirm_account(serializer.instance, 'TEACHER')

        return Response({'msg': 'Teacher created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        search = request.GET.get('search', None)
        teachers = Teacher.objects.all().order_by('-created_at')
        if search:
            teachers = teachers.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
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
                'date_of_birth': teacher.date_of_birth,
                'department': teacher.department,
                'specialization': teacher.specialization
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
        return Response({'msg': 'Teacher updated successfully'}, status=status.HTTP_200_OK)

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


@api_view(['POST'])
@permission_classes([])
def reset_password_confirm_link(request):
    data_request = request.data
    if data_request['token']:
        try:
            decode_payload = AccessToken(data_request['token'])
            payload = decode_payload.payload
        except Exception as ex:
            raise ValidationError({'token': [ex]})
        new_password = data_request['password']
        validate_password(new_password)
        user = User.objects.get(id=payload['user_id'])
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def student_api(request):
    if request.method == 'POST':
        data = request.data.copy()
        if User.objects.filter(email=data['email']).count() > 0:
            raise ValidationError({'msg': "Email already exist"})

        data['date_of_birth'] = datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date()
        data['is_student'] = True
        data['is_active'] = True
        password = Student.objects.make_random_password()
        data['password'] = password
        # import pdb; pdb.set_trace()

        serializer = StudentSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response({'msg': 'Student created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        search = request.GET.get('search', None)
        students = Student.objects.all().order_by('-created_at')
        if search:
            students = students.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        data = []
        for student in students:
            data.append({
                'id': student.id,
                # 'avatar': teacher.avatar if teacher.avatar else '',
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone_number': student.phone_number,
                'date_of_birth': student.date_of_birth,
                'guardian_name': student.guardian_name,
                'guardian_contact': student.guardian_contact,
                'enrollment_status': student.enrollment_status,
                'batch_year': student.batch_year

            })
        return paginated_queryset_response(data, request)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def upload_student_image(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    files = request.FILES.getlist('images')

    if not files:
        return Response({'msg': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    created_images = []
    for file in files:
        image_instance = StudentImage.objects.create(student=student, image=file)
        created_images.append(StudentImageSerializer(image_instance).data)

    student_picture_embedding(student)

    return Response({
        'msg': f'{len(files)} image(s) uploaded successfully',
        'images': created_images
    }, status=status.HTTP_201_CREATED)

@api_view(['PATCH', 'GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def student_by_id_api(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'PATCH':
        data = request.data

        for field_name, field_value in data.items():
            if hasattr(Student, field_name):
                setattr(student, field_name, field_value)

        student.save()
        return Response({'msg': 'Student updated successfully'}, status=status.HTTP_200_OK)

    if request.method == 'GET':
        data = {
            'id': student.id,
            # 'avatar': teacher.avatar if teacher.avatar else '',
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone_number': student.phone_number,
            'date_of_birth': student.date_of_birth,
            'guardian_name': student.guardian_name,
            'guardian_contact': student.guardian_contact,
            'enrollment_status': student.enrollment_status,
            'batch_year': student.batch_year
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        student.delete()
        return Response({'msg': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def class_api(request):
    if request.method == 'POST':
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        search = request.GET.get('search', None)
        classes = Class.objects.all().order_by('-created_at')
        if search:
            classes = classes.filter(Q(name__icontains=search) | Q(block__icontans=search))

        result = []

        for one_class in classes:
            result.append({
                'id': one_class.id,
                'name': one_class.name,
                'block': one_class.block,
                'cameras': [
                    {
                        'id': str(camera.id),
                        'name': camera.name,
                        'ip_address': camera.ip_address,
                    }
                    for camera in one_class.cameras.all()
                ]
            })
        return paginated_queryset_response(result, request)

@api_view(['PATCH', 'GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def class_by_id_api(request, class_id):
    one_class = get_object_or_404(Class, id=class_id)

    if request.method == 'PATCH':
        serializer = ClassSerializer(one_class, data=request.data, partial=True)  # partial=True allows PATCH
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Student updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        data = {
            'id': one_class.id,
            'name': one_class.name,
            'block': one_class.block,
            'cameras': [
                {
                    'id': cam.id,
                    'name': cam.name,
                    'ip_address': cam.ip_address
                }
                for cam in one_class.cameras.all()
            ]
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        one_class.delete()
        return Response({'msg': 'Class deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def course_api(request):
    if request.method == 'POST':
        print("📩 Incoming request data:", request.data)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("✅ Course saved successfully!")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
         print("❌ Serializer errors:", serializer.errors)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        courses = Course.objects.all().order_by('-created_at')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH', 'GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def course_by_id_api(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'PATCH':
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        course.delete()
        return Response({'msg': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)