"""Вью сеты апи"""
from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404

from reviews.models import Category, Title, Genre, Comment, Review, CustomUser
from .serializers import (CategorySerializer, TitleSerializer,
                          GenreSerializer, ReviewSerializer, CommentSerializer,
                          SignupSerializer, TokenSerializer, CustomUserSerializer)
from .permissions import OwnerOrReadOnly, IsAdminOrReadOnly, IsSuperUser, IsAdmin, IsModeratorOrReadOnly, IsOwnerOrAdmin, IsAuthenticatedOrReadOnly
from rest_framework import permissions


User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    """Класс категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = IsAdminOrReadOnly,
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,),
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category', 'genre', 'name', 'year')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GenreViewSet(viewsets.ModelViewSet):
    """Класс жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsOwnerOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс отзывов."""

    permission_classes = (OwnerOrReadOnly,)
    serializer_class = ReviewSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title__id',)

    def get_title(self):
        """Возвращает объект Title по 'title_id'."""
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

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
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comment.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class SignupView(APIView):
    """Регистрация пользователя и отправка confirmation_code."""
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        # Создание или получение пользователя
        user, created = CustomUser.objects.get_or_create(username=username, email=email)

        # Генерация confirmation code
        confirmation_code = default_token_generator.make_token(user)

        # Отправка email с confirmation code
        try:
            send_mail(
                subject="Код подтверждения для YaMDB",
                message=f"Ваш код подтверждения: {confirmation_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception:
            return Response(
                {"detail": "Ошибка при отправке email. Попробуйте позже."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Возврат данных о созданном пользователе
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
