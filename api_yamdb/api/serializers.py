from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from datetime import datetime

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre, CustomUser

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для CustomUser."""

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    class Meta:
        model = User
        fields = ('username', 'email')  # Указываем нужные поля из модели

    def validate_username(self, value):
        """Дополнительная валидация поля username."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' использовать запрещено."
            )
        return value


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
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'category'),
                message='Такое произведение уже '
                        'присутствует в указанной категории!'
            )
        ]
    
    def validate_year(self, value):
        """Проверка, что год выпуска не больше текущего."""
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!'
            )
        return value

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        num_score = reviews.count()
        if num_score == 0:
            return None
        all_score = sum(review.score for review in reviews)
        return round(all_score / num_score, 0)

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        # Извлекаем поле 'category', так как оно передается как объект, а не как слаг
        category = validated_data.pop('category')

        # Создаем объект Title
        title = Title.objects.create(**validated_data, category=category)

        # Связываем жанры с произведением
        for genre in genres:
            TitleGenre.objects.create(
                genre=genre, title=title
            )

        return title

    
    def update(self, instance, validated_data):
        genres = validated_data.pop('genre', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)      
        instance.save()

        if genres is not None:
            instance.genres.clear()
            for genre in genres:
                current_genre = Genre.objects.get(genre)
                TitleGenre.objects.create(genre=current_genre, title=instance)

        return instance


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    
    class Meta:
        model = Review
        fields = ('text', 'author', 'score', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Вы уже оставили отзыв на это произведение!'
            )
        ]
