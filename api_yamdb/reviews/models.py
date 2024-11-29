import re
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint

USER_ROLE = 'user'
MODERATOR_ROLE = 'moderator'
ADMIN_ROLE = 'admin'

ROLE_CHOICES = [
    (USER_ROLE, 'User'),
    (MODERATOR_ROLE, 'Moderator'),
    (ADMIN_ROLE, 'Admin'),
]


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(
            "Нельзя использовать 'me' в качестве имени пользователя.")

    if not re.match(r'^[\w]+$', username):
        raise ValidationError("Имя пользователя может содержать только буквы, "
                              "цифры и подчеркивания.")


class UserModel(AbstractUser):
    """Кастомная модель пользователя."""
    role = models.CharField(
        max_length=max(len(role[0]) for role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER_ROLE,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username],  # Подключаем нашу валидирующую функцию
        verbose_name='Username'
    )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name[:50]


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name[:50]


class Title(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='titles'
    )
    genre = models.ManyToManyField(
        'Genre',
        through='TitleGenre',
        verbose_name='Жанры',
        related_name='titles'
    )
    name = models.CharField(max_length=256)
    description = models.TextField(
        blank=True, null=True, verbose_name='Описание')
    year = models.IntegerField(verbose_name='Год публикации')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_title_category')
        ]
        ordering = ['id']

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='title_genres'
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
        verbose_name='Жанр',
        related_name='genre_titles'
    )

    class Meta:
        db_table = 'reviews_titlegenre'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]
        verbose_name = 'Связь произведение-жанр'
        verbose_name_plural = 'Связи произведение-жанр'
        ordering = ['id']

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(Title, related_name='reviews',
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')
    text = models.CharField(max_length=256, verbose_name='Название')
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title_review'
            ),
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']

    def clean(self):
        if Review.objects.filter(
            author=self.author, title=self.title
        ).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение!')

    def __str__(self):
        return f'Ревью от {self.author} на {self.title}'


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    title = models.ForeignKey(Title, related_name='comments',
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')
    review = models.ForeignKey(Review, related_name='comments',
                               on_delete=models.CASCADE,
                               verbose_name='Отзыв')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий от {self.author} на {self.review}'
