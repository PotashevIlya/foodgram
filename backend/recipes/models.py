from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, MAX_PASSWORD_LENGTH,
    MIN_COOKING_TIME, MAX_RECIPE_NAME_LENGTH, MIN_AMOUNT
)
from .validators import validate_username


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
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='subscribers'
    )
    author = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='followings'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_subscriber_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписка {self.subscriber} на {self.author}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=32,
        unique=True,
        help_text='Укажите название'
    )
    slug = models.SlugField(
        verbose_name='Ярлык',
        max_length=32,
        unique=True,
        help_text='Укажите название'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=128,
        help_text='Укажите название продукта'
    )
    measurement_unit = models.CharField(
        verbose_name='Мера',
        max_length=64,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, ед.измерения - {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_RECIPE_NAME_LENGTH,
        help_text='Укажите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        help_text='Загрузите изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Продукты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Укажите время больше {MIN_COOKING_TIME} мин.'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name}. Автор - {self.author}.'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Игнредиент'
    )
    amount = models.IntegerField(
        verbose_name='Мера',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Минимальное количество - {MIN_AMOUNT}'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        default_related_name = 'recipeingredients'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class UserRecipeBaseModel(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_%(class)s'
            )
        ]
        ordering = ('-recipe__pub_date',)
        default_related_name = '%(class)s'

    def __str__(self):
        return f'{self.recipe} у {self.user}'


class Favourite(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
