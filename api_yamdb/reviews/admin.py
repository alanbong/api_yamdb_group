from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'bio')  # поля для отображения
    list_filter = ('role',)  # Фильтрация по ролям
    search_fields = ('username', 'email')  # Поиск по имени и email
