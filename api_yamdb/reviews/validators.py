import re
from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(
            "Нельзя использовать 'me' в качестве имени пользователя.")

    if not re.match(r'^[\w]+$', username):
        raise ValidationError("Имя пользователя может содержать только буквы, "
                              "цифры и подчеркивания.")
