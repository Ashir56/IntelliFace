from rest_framework import permissions


class IsTeacher(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_teacher', False))