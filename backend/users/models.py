from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH = 150
MAX_LENGTH_FOR_EMAIL = 254


class User(AbstractUser):
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_LENGTH_FOR_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH,
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_LENGTH,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
