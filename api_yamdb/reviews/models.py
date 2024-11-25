from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Categories(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def str(self):
        return self.name[:50]


class Titles(models.Model):
    category = models.ForeignKey(
        Categories, related_name='title',
        on_delete=models.CASCADE,
        verbose_name='Категория')
    name = models.CharField(max_length=200)
    year = models.IntegerField()

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_title_category')
        ]

    def str(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=50, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def str(self):
        return self.name[:50]


class Reviews(models.Model):
    ...sdsdsds


class Comments(models.Model):
    ...
