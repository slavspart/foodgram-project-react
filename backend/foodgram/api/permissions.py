from rest_framework import permissions, exceptions


class UpdateRestriction(permissions.BasePermission):
    """Класс для запрета put метода"""
    def has_permission(self, request, view):
        if request.method == 'PUT':
            raise exceptions.MethodNotAllowed('PUT')
        return True
