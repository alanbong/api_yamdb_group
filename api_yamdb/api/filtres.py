import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтрация произведений по полям года, жанра и категории."""

    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__slug',
                                         lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['year', 'name', 'genre', 'category']
