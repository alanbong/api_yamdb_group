"""Вью сеты апи"""
from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.exceptions import PermissionDenied

from reviews.models import Category, Title, Genre, Comment, Review, CustomUser
from .serializers import (CategorySerializer, TitleSerializer,
                          GenreSerializer, ReviewSerializer, CommentSerializer,
                          SignupSerializer, TokenSerializer, CustomUserSerializer)
from .permissions import IsAdmin, CommentsPermission, IsAdminOrReadOnly, UserMePermissions
from rest_framework import permissions
from rest_framework.filters import SearchFilter


User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


class UserMeViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для изменения профиля.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [UserMePermissions]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.validated_data.pop('role', None)
        serializer.save()


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Класс категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    search_fields = ('category', 'genre', 'name', 'year')
    lookup_field = 'id'
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        """
        Отфильтровать произведения по году, жанру и категории, если указаны в запросе.
        """
        queryset = Title.objects.all()

        # Фильтрация по году (если параметр 'year' передан)
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(year=year)

        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name=name)

        # Фильтрация по жанрам (по слагам)
        genre_slug = self.request.query_params.get('genre', None)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)

        # Фильтрация по категориям (по слагам)
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Класс жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс отзывов."""

    permission_classes = (CommentsPermission,)
    serializer_class = ReviewSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Review.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'review_id'

    def get_object(self):
        """
        Переопределяет стандартный метод для поиска объекта.
        """
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(Review, id=review_id, title_id=title_id)

    def get_queryset(self):
        """
        Возвращает отзывы для указанного произведения.
        """
        title_id = self.kwargs.get('title_id')
        return self.queryset.filter(title_id=title_id)

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

    permission_classes = (CommentsPermission,)
    serializer_class = CommentSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id', 'reviews__id')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Возвращает объект Review по 'review_id'."""
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review(), title=self.get_title())


class SignupView(APIView):
    """Регистрация пользователя и отправка confirmation_code."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user, _ = User.objects.get_or_create(username=username, email=email)

        confirmation_code = default_token_generator.make_token(user)

        try:
            send_mail(
                subject="Код подтверждения для YaMDB",
                message=f"Ваш код подтверждения: {confirmation_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            return Response(
                {"detail": f"Ошибка при отправке email: {str(e)}. Попробуйте позже."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"username": username, "email": email},
            status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """Получение JWT-токена на основе username и confirmation_code."""
    permission_classes = (AllowAny,)
    # search_fields

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        # Проверка соответсвия кода у пользователя
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'detail': 'Неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
