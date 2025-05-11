from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import uuid
from django.contrib.auth.password_validation import validate_password
from string import ascii_lowercase, ascii_uppercase, digits, punctuation


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if 'groups' in extra_fields:
            extra_fields.pop('groups')

        if 'user_permissions' in extra_fields:
            extra_fields.pop('user_permissions')

        if not email:
            raise ValueError('The given email must be set.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        validate_password(password)
        user.set_password(password)
        user.username = email
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)

    def make_random_password(self, length=10):
        rand_pass = []
        for i in range(0, 2):
            rand_pass.append(random.choice(digits))
            rand_pass.append(random.choice(ascii_lowercase))
            rand_pass.append(random.choice(punctuation))
            rand_pass.append(random.choice(ascii_uppercase))

        random.shuffle(rand_pass)
        password = ''.join(rand_pass)
        return password


class User(AbstractUser):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        null=True, blank=True, max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(
        null=True, blank=True, max_length=255)
    city = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        null=True,
        verbose_name=u'Created at')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.
        This string is used when a `User` is printed in the console.
        """
        return self.email


class Teacher(User):
    department = models.CharField(max_length=100)
    # courses_taught = models.ManyToManyField('Course', related_name='teachers')
    joining_date = models.DateField()
    specialization = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"


class Student(User):
    # courses_enrolled = models.ManyToManyField('Course', related_name='students')
    batch_year = models.PositiveIntegerField()
    grade_level = models.CharField(max_length=20, null=True, blank=True)
    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_contact = models.CharField(max_length=20, null=True, blank=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    attendance_percentage = models.FloatField(default=0.0)
    extra_curricular = models.TextField(null=True, blank=True)
    enrollment_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')],
        default='active'
    )

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Batch {self.batch_year})"
