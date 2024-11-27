from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        if not request.user.is_admin:
            print('бляяяя')
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class IsModeratorOrReadOnly(BasePermission):
    """Доступ для модераторов или только чтение."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_moderator


class IsOwnerOrAdmin(BasePermission):
    """Доступ только владельцу объекта или админу."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_admin



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
