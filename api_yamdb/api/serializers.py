from rest_framework import serializers
from django.contrib.auth import get_user_model

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
