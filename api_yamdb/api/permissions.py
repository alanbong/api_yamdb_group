from rest_framework.permissions import (BasePermission, SAFE_METHODS,
                                        AllowAny, IsAuthenticatedOrReadOnly)


class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    """Доступ для модераторов или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or (
                request.user.is_authenticated and (
                    request.user.is_superuser or request.user.is_admin))
        )


class CommentsPermission(IsAuthenticatedOrReadOnly):
    """
    Доступ для чтения всем, а для редактирования автору,
    модератору или администратору.
    """

    def has_object_permission(self, request, view, obj):
        # Используем базовую проверку для безопасных методов
        if request.method in SAFE_METHODS:
            return True

        # Проверяем, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return False

        # Для методов PATCH и DELETE проверяем права на объект
        if request.method in ('PATCH', 'DELETE'):
            # Разрешаем редактирование или удаление, если пользователь автор
            if obj.author == request.user:
                return True
            if getattr(request.user, 'is_moderator', False):
                return True
            if getattr(request.user, 'is_admin', False):
                return True

            return False

        # Для всех остальных методов, если не безопасные, доступ не даем
        return False


class UserMePermissions(AllowAny):

    def has_permission(self, request, view):
        if request.method in ['POST', 'PATCH']:
            if request.user.is_authenticated:
                return request.user.role in ['user', 'moderator', 'admin']
            return False

        if request.user.is_authenticated:
            return request.user.role == 'user'

        return False
