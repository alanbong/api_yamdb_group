from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .constants import (
    MAX_LENGTH_256, MAX_LENGTH_150, MAX_LENGTH_50,
    USER_ROLE, MODERATOR_ROLE, ADMIN_ROLE,
    MIN_VALUE, MAX_VALUE
)
from .validators import validate_username


ROLE_CHOICES = [
    (USER_ROLE, 'User'),
    (MODERATOR_ROLE, 'Moderator'),
    (ADMIN_ROLE, 'Admin'),
]


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
        max_length=MAX_LENGTH_150,
        unique=True,
        validators=[validate_username],
        verbose_name='Username'
    )

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return str(self.username)


class NameSlugModel(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_256,
                            verbose_name='Название')

    slug = models.SlugField(unique=True,
                            max_length=MAX_LENGTH_50,
                            verbose_name='Идентификатор')

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return str(self.name)[:MAX_LENGTH_50]


class Category(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='titles'
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанры',
        related_name='titles'
    )
    name = models.CharField(max_length=MAX_LENGTH_256)
    description = models.TextField(
        blank=True, verbose_name='Описание')
    year = models.IntegerField(verbose_name='Год публикации')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_title_category')
        ]
        ordering = ['category', 'name', 'year']

    def __str__(self):
        return str(self.name)


class Review(models.Model):
    title = models.ForeignKey(Title, related_name='reviews',
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')
    text = models.CharField(max_length=MAX_LENGTH_256, verbose_name='Название')
    score = models.IntegerField(validators=[MinValueValidator(MIN_VALUE),
                                            MaxValueValidator(MAX_VALUE)])

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
