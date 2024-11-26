from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre

User = get_user_model()


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
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

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
    
    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category = validated_data.pop('category')
        current_category, _ = Category.objects.get_or_create(**category)
        validated_data['category'] = current_category
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre, _ = Genre.objects.get_or_create(**genre)
            TitleGenre.objects.create(
                genre=current_genre, title=title)
        return title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Вы уже оставили отзыв на это произведение!'
            )
        ]
