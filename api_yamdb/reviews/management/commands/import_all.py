import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Genre, Title, Review, Comment
)

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.import_categories()
        self.import_genres()
        self.import_titles()
        self.import_users()
        self.import_reviews()
        self.import_comments()
        self.import_genre_titles()

    def import_categories(self):
        file_path = 'static/data/category.csv'
        categories = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                categories.append(Category(**row))
        Category.objects.bulk_create(categories, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Импорт категорий завершён.'))

    def import_genres(self):
        file_path = 'static/data/genre.csv'
        genres = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                genres.append(Genre(**row))
        Genre.objects.bulk_create(genres, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Импорт жанров завершён.'))

    def import_titles(self):
        file_path = 'static/data/titles.csv'
        titles = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                titles.append(Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category
                ))
        Title.objects.bulk_create(titles, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Импорт произведений завершён.'))

    def import_users(self):
        file_path = 'static/data/users.csv'
        users = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(User(**row))
        User.objects.bulk_create(users, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Импорт пользователей завершён.'))

    def import_reviews(self):
        file_path = 'static/data/review.csv'
        reviews = []

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                reviews.append(Review(
                    id=row['id'],
                    title_id=title.id,  # Указываем title_id
                    text=row['text'],
                    score=row['score'],
                    author=author,
                    pub_date=row['pub_date']
                ))

        Review.objects.bulk_create(reviews, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Импорт отзывов завершён!'))

    def import_comments(self):
        file_path = 'static/data/comments.csv'
        comments = []

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                review = Review.objects.get(id=row['review_id'])
                title = review.title
                author = User.objects.get(id=row['author'])

                comments.append(Comment(
                    id=row['id'],
                    review=review,
                    title=title,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date']
                ))

        Comment.objects.bulk_create(comments, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS('Импорт комментариев завершён.'))

    def import_genre_titles(self):
        file_path = 'static/data/genre_title.csv'
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                genre = Genre.objects.get(id=row['genre_id'])
                title = Title.objects.get(id=row['title_id'])
                title.genre.add(genre)
        self.stdout.write(
            self.style.SUCCESS('Импорт связей жанр-произведение завершён.'))
