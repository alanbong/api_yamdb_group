import re

from django.core.validators import RegexValidator
from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from datetime import datetime
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre, CustomUser


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для CustomUser."""

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Использовать имя "me" запрещено.')
        if len(value) > 150:
            raise serializers.ValidationError('Имя не должно быть длиннее 150 символов.')
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Username может содержать только буквы, цифры и символы @/./+/-/_'
            )
        return value


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
                RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Username может содержать только буквы, цифры и символы @/./+/-/_'
            )
        ]
    )

    def validate_username(self, value):
        """
        Проверяем, что username не является зарезервированным.
        """
        if value == "me":
            raise serializers.ValidationError(
                "Имя пользователя 'me' использовать нельзя."
            )
        return value

    def validate(self, data):
        """
        Проверяем пользователя в базе данных.
        Если пользователь с совпадающим username и email существует,
        пропускаем проверку уникальности.
        """
        username = data.get('username')
        email = data.get('email')

        user = User.objects.filter(Q(username=username) | Q(email=email)).first()

        if user:
            if user.username != username and user.email == email:
                raise serializers.ValidationError(
                    {"email": "Этот email уже используется с другим username."}
                )

            if user.email != email and user.username == username:
                raise serializers.ValidationError(
                    {"username": "Этот username уже используется с другим email."}
                )

            if user.username == username and user.email == email:
                return data

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Укажите username."
    )
    confirmation_code = serializers.CharField(
        required=True,
        help_text="Код подтверждения, отправленный на email."
    )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""
    genre = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all(), many=True, required=True)
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all(), required=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'category'),
                message='Такое произведение уже присутствует в указанной категории!'
            )
        ]

    def validate_year(self, value):
        """Проверка, что год выпуска не больше текущего."""
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError('Год выпуска не может быть больше текущего!')
        return value

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        num_score = reviews.count()
        if num_score == 0:
            return None
        all_score = sum(review.score for review in reviews)
        return round(all_score / num_score, 0)

    def to_representation(self, instance):
        """Переопределяем метод to_representation для корректного представления жанров и категорий."""
        # Получаем стандартное представление данных
        representation = super().to_representation(instance)

        # Преобразуем жанры в нужный формат (список словарей)
        representation['genre'] = [{"name": genre.name, "slug": genre.slug} for genre in instance.genre.all()]
        
        # Преобразуем категорию в нужный формат (словарь)
        representation['category'] = {
            "name": instance.category.name,
            "slug": instance.category.slug
        }

        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        title = self.context['view'].get_title()
        if request.method == 'POST' and Review.objects.filter(
            author=request.user, title=title
        ).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение.')
        return data
