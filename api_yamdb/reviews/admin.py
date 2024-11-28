"""Настройки администратора"""
from django.contrib import admin

from .models import CustomUser, Category, Genre, Title


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
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

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])

    display_genres.short_description = 'Жанры'
