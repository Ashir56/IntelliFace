from django.urls import path
from .views import (MyTokenObtainPairView, MyTokenRefreshView, course_api, course_by_id_api, index, teacher_api,
                    teacher_by_id_api, reset_password_confirm_link, student_api, student_by_id_api, class_api,
                    class_by_id_api, upload_student_image, course_students_api, course_mark_attendance_api, start_attendance_api, stop_attendance_api,
                    lecture_api, get_attendance_details_by_lecture, process_lecture_recognition, ml_status, set_password_api,
                    get_count, get_lecture_by_id, cron_capture_snapshots)

app_name = 'users'

urlpatterns = [
    path('', index, name='home'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('teacher/', teacher_api, name='teacher api'),
    path('student/', student_api, name='student api'),
    path('class/', class_api, name='class api'),
    path('count/', get_count, name='get metdata count api'),
    path('set-password/', set_password_api, name='set_password'),
    path('teacher/<str:teacher_id>/', teacher_by_id_api, name='teacher by id api'),
    path('student/<str:student_id>/', student_by_id_api, name='student by id api'),
    path('class/<str:class_id>/', class_by_id_api, name='class by id api'),
    path('reset-password-confirm/', reset_password_confirm_link, name='reset_password_confirm_link'),
    path('student/<str:student_id>/upload-images/', upload_student_image, name='upload_student_image'),
    path('course/', course_api, name='course api'),
    path('course/<str:course_id>/students/', course_students_api, name='course students api'),
    path('course/<str:course_id>/', course_by_id_api, name='course by id api'),
    path('course/<str:course_id>/attendance/', course_mark_attendance_api, name='course mark attendance'),
    path('start-attendance/', start_attendance_api, name='start_attendance_api'),
    path('stop-attendance/<str:lecture_id>/', stop_attendance_api, name='stop_attendance_api'),
    path('lecture/', lecture_api, name='lecture_api'),
    path('lecture/<str:lecture_id>/', get_lecture_by_id, name='lecture_by_id_api'),
    path('attendance/<str:lecture_id>/', get_attendance_details_by_lecture, name='get_attendance_details_by_lecture'),
    path('lecture/<str:lecture_id>/process-recognition/', process_lecture_recognition, name='process_lecture_recognition'),
    path('ml-status/', ml_status, name='ml_status'),
    path('cron/capture-snapshots/', cron_capture_snapshots, name='cron_capture_snapshots'),
]
