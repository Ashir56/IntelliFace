# Generated by Django 5.1.7 on 2025-05-11 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_student_student_id_remove_teacher_employee_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='availability_hours',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='experience_years',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='office_number',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='qualification',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='research_papers',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='salary',
        ),
    ]
