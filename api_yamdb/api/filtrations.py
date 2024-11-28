from django_filters import rest_framework as filters
from .models import Title
from rest_framework import filters
import django_filters


class TitleFilter(filters.FilterSet):
    """Фильтрация по жанрам (слаг) и категории."""
    genre = filters.CharFilter(field_name='genre__slug', lookup_expr='iexact')  # фильтрация по слагу жанра
    category = filters.CharFilter(field_name='category__slug', lookup_expr='iexact')  # фильтрация по слагу категории

    class Meta:
        model = Title
        fields = ['genre', 'category']
