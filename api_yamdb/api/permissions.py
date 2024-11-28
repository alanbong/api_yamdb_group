from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModeratorOrReadOnly(BasePermission):
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
        if request.method == 'POST':
            return request.user.is_authenticated

        # Проверка является ли пользователь автором, модератором или админом
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            comment = view.get_object()  # Получаем объект комментария
            if (request.user == comment.author or request.user.is_staff
                    or request.user.is_superuser):
                return True
        return False
