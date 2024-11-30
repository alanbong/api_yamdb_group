from datetime import datetime
import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(
            "Нельзя использовать 'me' в качестве имени пользователя.")

    if not re.match(r'^[\w]+$', username):
        raise ValidationError("Имя пользователя может содержать только буквы, "
                              "цифры и подчеркивания.")


def validate_year(value):
    """Проверка, что год выпуска не больше текущего."""
    current_year = datetime.now().year
    if value > current_year:
        raise serializers.ValidationError(
            'Год выпуска не может быть больше текущего!')
    return value
