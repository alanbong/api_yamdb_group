from rest_framework.permissions import BasePermission, SAFE_METHODS, AllowAny




class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    """Доступ для модераторов или только чтение."""

    def has_permission(self, request, view):
        # Разрешаем доступ для всех пользователей для безопасных методов
        if request.method in SAFE_METHODS:
            return True

        # Если пользователь анонимный, не проверяем его роль
        if not request.user.is_authenticated:
            return False

        # Для методов POST, PUT, DELETE проверяем роль пользователя
        if request.user.is_superuser or request.user.role == 'admin':
            return True

        return False


class CommentsPermission(BasePermission):
    """
    Доступ для чтения всем, а для редактирования автору, модератору или администратору.
    """
    def has_permission(self, request, view):
        # Чтение доступно всем
        if request.method in SAFE_METHODS:
            return True

        # Проверяем авторизацию для остальных методов
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Чтение доступно всем
        if request.method in SAFE_METHODS:
            return True

        # Редактировать может автор, модератор или администратор
        return (
            request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )


class UserMePermissions(AllowAny):

    def has_permission(self, request, view):
        # Разрешаем доступ всем аутентифицированным пользователям для POST и PATCH
        if request.method in ['POST', 'PATCH']:
            # Проверяем, что пользователь аутентифицирован и у него есть роль
            if request.user.is_authenticated:
                # Разрешаем доступ только пользователям с ролями 'user', 'moderator' или 'admin'
                return request.user.role in ['user', 'moderator', 'admin']
            return False

        # Для остальных методов проверяем, что пользователь аутентифицирован и его роль 'user'
        if request.user.is_authenticated:
            return request.user.role == 'user'

        return False
