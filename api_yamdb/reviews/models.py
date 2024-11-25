import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


RATING_CHOICES = [(i, i) for i in range(1, 11)]
ROLE_CHOICES = [
    ('user', 'User'),
    ('moderator', 'Moderator'),
    ('admin', 'Admin'),
]


class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    confirmation_code = models.CharField(max_length=20, blank=True)

    def generate_confirmation_code(self):
        """Генерирует новый уникальный код подтверждения."""
        self.confirmation_code = str(uuid.uuid4())
        self.save(update_fields=['confirmation_code'])


class Categories(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:50]


class Genres(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:50]


class Titles(models.Model):
    category = models.ForeignKey(
        Categories, related_name='title',
        on_delete=models.CASCADE,
        verbose_name='Категория')
    genre = models.ManyToManyField(
        Genres, related_name='title',
        verbose_name='Жанр')
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

    def __str__(self):
        return self.name


class Reviews(models.Model):
    title_id = models.ForeignKey(Titles, related_name='reviews',
                                 on_delete=models.CASCADE,
                                 verbose_name='Произведение')
    text = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')
    score = models.IntegerField(choices=RATING_CHOICES)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Ревью от {self.author} на {self.title_id}'


class Comments(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    title_id = models.ForeignKey(Titles, related_name='comments',
                                 on_delete=models.CASCADE,
                                 verbose_name='Произведение')
    review_id = models.ForeignKey(Reviews, related_name='comments',
                                  on_delete=models.CASCADE,
                                  verbose_name='Отзыв')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.author} на {self.review_id}'
