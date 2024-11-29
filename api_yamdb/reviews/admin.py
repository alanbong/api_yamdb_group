"""Настройки администратора"""
from django.contrib import admin

from .models import UserModel, Category, Genre, Title


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'bio', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'year', 'description', 'display_genres', 'category'
    )
    list_filter = ('name', 'year', 'genre', 'category')
    search_fields = ('name',)

    @admin.display(description='Жанры')
    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])
