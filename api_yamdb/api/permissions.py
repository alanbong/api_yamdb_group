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
    Доступ для чтения всем, а для редактирования стафу и автору
    """

    def has_permission(self, request, view):
        # Просмотр комментариев и отдельных комментариев доступен всем
        if request.method in SAFE_METHODS:
            return True

        # Если пользователь анонимный, не проверяем его роль
        if not request.user.is_authenticated:
            return False

        # Создание комментария доступно всем, кроме анонимных пользователей
        if request.method == 'POST' and request.user.is_authenticated:
            return True

        # Проверка является ли пользователь автором, модератором или админом
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            comment = view.get_object()  # Получаем объект комментария
            if (request.user == comment.author or request.user.is_moderator or request.user.is_admin):
                return True
        return False


class UserMePermissions(AllowAny):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        if request.method in ['POST', 'PATCH']:
            return request.user.role in ['user', 'moderator', 'admin']

        if request.method == 'DELETE':
            return request.user.role in ['moderator', 'admin']
