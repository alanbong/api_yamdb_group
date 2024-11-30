from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Avg

from reviews.models import Category, Title, Genre, Review
from api.serializers import (
    CategorySerializer, TitleSerializer, GenreSerializer, ReviewSerializer,
    CommentSerializer, SignupSerializer, TokenSerializer, UserModelSerializer,
    TitleSerializerForRead
)
from api.permissions import (
    IsAdmin, IsStuffOrAuthor, IsAdminOrReadOnly
)
from api.baseviewset import BaseCategoryGenreViewSet
from api.filtres import TitleFilter


User = get_user_model()


class UserModelViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username', 'email')
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    @action(detail=False, methods=('get', 'patch'),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Эндпоинт для изменения профиля текущего пользователя."""
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user,
                                             data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data.pop('role', None)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(BaseCategoryGenreViewSet):
    """Класс категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return self.serializer_class


class GenreViewSet(BaseCategoryGenreViewSet):
    """Класс жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return self.serializer_class


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name',)
    ordering_fields = ('name', 'year')
    ordering = ('name',)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return TitleSerializerForRead
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс отзывов."""

    permission_classes = (IsStuffOrAuthor,)
    serializer_class = ReviewSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Review.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        """Возвращает отзывы для указанного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def get_title(self):
        """
        Возвращает объект произведения по его id из URL.
        """
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def perform_create(self, serializer):
        """
        Устанавливает автора и произведение при создании отзыва.
        """
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Класс комментов."""

    permission_classes = (IsStuffOrAuthor,)
    serializer_class = CommentSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id', 'reviews__id')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Возвращает объект Review по 'review_id'."""
        return get_object_or_404(Review, id=self.kwargs['review_id'],
                                 title_id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(
            author=self.request.user,
            review=review,
        )


class SignupView(APIView):
    """Регистрация пользователя и отправка confirmation_code."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"username": user.username, "email": user.email},
            status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """Получение JWT-токена на основе username и confirmation_code."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data['username'])
        token = AccessToken.for_user(user)

        return Response({'token': str(token)}, status=status.HTTP_200_OK)
