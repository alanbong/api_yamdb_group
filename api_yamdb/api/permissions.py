from rest_framework.permissions import BasePermission, SAFE_METHODS, AllowAny


class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    """Доступ для модераторов или только чтение."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role == 'admin':
            return True

        return False


class CommentsPermission(BasePermission):
    """
    Доступ для чтения всем, а для редактирования автору,
    модератору или администратору.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.method in ('PATCH', 'DELETE'):
            obj = view.get_object()

            if obj.author == request.user:
                return True
            if getattr(request.user, 'is_moderator', False):
                return True
            if getattr(request.user, 'is_admin', False):
                return True

            return False

        return True


class UserMePermissions(AllowAny):

    def has_permission(self, request, view):
        if request.method in ['POST', 'PATCH']:
            if request.user.is_authenticated:
                return request.user.role in ['user', 'moderator', 'admin']
            return False

        if request.user.is_authenticated:
            return request.user.role == 'user'

        return False
