"""Настройки администратора"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Genre, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # поля для отображения
    prepopulated_fields = {'slug': ('name',)} #автоматическое создания слага
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # поля для отображения
    prepopulated_fields = {'slug': ('name',)} #автоматическое создания слага
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'year', 'description', 'display_genres', 'category'
    ) # поля для отображения
    list_filter = ('name', 'year', 'genre', 'category')  # Фильтрация
    search_fields = ('name',)

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])

    display_genres.short_description = 'Жанры'
  

@admin.register(CustomUser)

class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""
    list_display = ('username', 'email', 'role', 'bio')
    list_filter = ('role',)
    search_fields = ('username', 'email')

    
# CustomUser._meta.app_label = "auth"
