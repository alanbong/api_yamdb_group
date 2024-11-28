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

        # Для методов записи/обновления/удаления проверяем аутентификацию
        if not request.user.is_authenticated:
            return False

        # Дополнительная проверка объекта для методов, требующих его
        if request.method in ('PATCH', 'DELETE'):
            # Получаем объект через `get_object` во ViewSet
            obj = view.get_object()

            # Проверяем, является ли пользователь автором, модератором или администратором
            if obj.author == request.user:
                return True
            if getattr(request.user, 'is_moderator', False):
                return True
            if getattr(request.user, 'is_admin', False):
                return True

            # Если пользователь не имеет прав, возвращаем False
            return False

        return True


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
