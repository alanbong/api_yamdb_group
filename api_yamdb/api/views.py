from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import title
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import viewsets, filters
from rest_framework.generics import get_object_or_404

from reviews.models import Categories, Titles, Genres
from .serializers import (CategoriesSerializer, TitlesSerializer, GenresSerializer, ReviewsSerializer, CommentSerializer, SignupSerializer, TokenSerializer)
from .permissions import OwnerOrReadOnly


User = get_user_model()


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


class SignupView(APIView):
    """Регистрация пользователя и отправка confirmation_code."""
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # Создание или получение пользователя
        user, created = User.objects.get_or_create(
            email=email, username=username
        )

        # Генерация нового confirmation_code
        confirmation_code = default_token_generator.make_token(user)

        # Отправка email
        try:
            send_mail(
                subject='Код подтверждения для YaMDB',
                message=f'Ваш код подтверждения: {confirmation_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception:
            return Response(
                {'detail': 'Ошибка при отправке письма. Попробуйте позже.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        detail_message = (
            ('Пользователь успешно зарегистрирован. '
             'Код подтверждения отправлен.')
            if created
            else ('Пользователь уже существует. '
                  'Новый код подтверждения отправлен.')
        )

        return Response(
            {'detail': detail_message},
            status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """Получение JWT-токена на основе username и confirmation_code."""
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
