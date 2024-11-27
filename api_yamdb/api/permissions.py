from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS


class OwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, post):
        return (request.method in permissions.SAFE_METHODS
                or post.author == request.user)


class IsAdminOrReadOnly(BasePermission):
    """
    Доступ для чтения всем, а для записи только администраторам.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSuperUser(BasePermission):
    """
    Доступ только для суперпользователей.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
