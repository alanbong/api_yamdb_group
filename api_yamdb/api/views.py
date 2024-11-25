from django.template.defaultfilters import title
from rest_framework import viewsets, filters
from rest_framework.generics import get_object_or_404

from reviews.models import Categories, Titles, Genres
from .serializers import (CategoriesSerializer, TitlesSerializer, GenresSerializer, ReviewsSerializer, CommentSerializer)
from .permissions import OwnerOrReadOnly


class CategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс категорий."""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitlesViewSet(viewsets.ModelViewSet):
    """Класс произведений."""

    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category', 'genre', 'name', 'year')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GenresViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс жанров."""

    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewsViewSet(viewsets.ModelViewSet):
    """Класс отзывов."""

    permission_classes = (OwnerOrReadOnly,)
    serializer_class = ReviewsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id',)

    def get_title(self):
        """Возвращает объект Title по 'title_id'."""
        return get_object_or_404(title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Переопределяем создание отзывов."""
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Класс комментов."""

    permission_classes = (OwnerOrReadOnly,)
    serializer_class = CommentSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id','reviews__id')

    def get_review(self):
        """Возвращает объект Review по 'review_id'."""
        return get_object_or_404(Reviews, pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comment.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())