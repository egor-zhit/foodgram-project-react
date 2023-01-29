from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import username_validator


class UserModel(AbstractUser):
    email = models.EmailField(
        'Электроная почта',
        max_length=250,
        unique=True
    )
    username = models.CharField(
        'Логин пользователя',
        max_length=100,
        unique=True,
        validators=(username_validator)
    )
    first_name = models.CharField(
        'Имя',
        max_length=100,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=100,
        blank=False
    )
