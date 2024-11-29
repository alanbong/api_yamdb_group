from rest_framework import viewsets, mixins, filters
from .permissions import IsAdminOrReadOnly


class BaseCategoryGenreViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """Базовый класс для вьюсетов категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_queryset(self):
        """Метод для получения queryset, переопределяется в наследниках."""
        raise NotImplementedError

    def get_serializer_class(self):
        """
        Метод для получения сериализатора,
        переопределяется в наследниках.
        """
        raise NotImplementedError
