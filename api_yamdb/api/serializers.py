from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from datetime import datetime

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для CustomUser."""

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def is_valid(self, raise_exception=False):
        """
        Переопределяем метод is_valid для проверки существующего пользователя.
        """
        # Получаем данные из контекста
        data = self.initial_data
        username = data.get('username')
        email = data.get('email')

        # Проверяем, существует ли пользователь с таким username и email
        user = CustomUser.objects.filter(username=username).first()
        if user:
            if user.email != email:
                raise serializers.ValidationError(
                    {
                        'username': 'Пользователь с таким username уже существует, но email не совпадает.',
                        'email': 'Пользователь с таким email уже существует, но username не совпадает.'
                    }
                )
            # Если пользователь существует и email совпадает, добавляем сообщение в контекст
            self._validated_data = {'username': username, 'email': email}
            self.context['user_exists'] = True
            return True

        # Если пользователь не найден, вызываем стандартную проверку
        return super().is_valid(raise_exception=raise_exception)



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
            return 0
        all_score = sum(review.score for review in reviews)
        return round(all_score / num_score, 0)
    
    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = Genre.objects.get(**genre)
            TitleGenre.objects.create(
                genre=current_genre, title=title)
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
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Вы уже оставили отзыв на это произведение!'
            )
        ]
