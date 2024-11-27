from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""
    list_display = ('username', 'email', 'role', 'bio')
    list_filter = ('role',)
    search_fields = ('username', 'email')


User._meta.app_label = "auth"
