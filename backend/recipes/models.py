from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_PASSWORD_LENGTH = 128


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=MAX_EMAIL_LENGTH,
        blank=False,
        null=False,
        unique=True,
        help_text='Укажите электронную почту'
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        help_text='Укажите имя пользователя',
        validators=(
            validate_username,
        )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_USERNAME_LENGTH,
        blank=False,
        null=False,
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_USERNAME_LENGTH,
        blank=False,
        null=False,
        help_text='Укажите фамилию'
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_PASSWORD_LENGTH,
        blank=False,
        null=False,
        help_text='Придумайте пароль'
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='recipes/images/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='subscriber'
    )
    following = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'following'),
                name='unique_subscriber_following'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=32,
        unique=True,
        blank=False,
        null=False,
        help_text='Укажите название тега'
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=32,
        unique=True,
        blank=False,
        null=False,
        help_text='Укажите слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
