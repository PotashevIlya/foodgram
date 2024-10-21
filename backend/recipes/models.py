from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_username

MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_PASSWORD_LENGTH = 128
MIN_COOKING_TIME = 1
MAX_RECIPE_NAME_LENGTH = 256


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

    def __str__(self):
        return f'Подписка {self.subscriber} на {self.following}'


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

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=128,
        blank=False,
        null=False,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=64,
        blank=False,
        null=False,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, ед.измерения - {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_RECIPE_NAME_LENGTH,
        blank=False,
        null=False,
        help_text='Укажите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images/',
        null=False,
        blank=False,
        help_text='Загрузите изображение рецепта'
    )
    text = models.TextField(verbose_name='Подробный рецепт')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'''Время приготовления не может быть меньше
                {MIN_COOKING_TIME} мин.'''
            ),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name}. Повар - {self.author}.'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт'
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Игнредиент'
                                   )
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'recipeingredients'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class RecipeShortURL(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    short_url = models.CharField(max_length=10, unique=True, verbose_name='Короткая ссылка')
    full_url = models.URLField(verbose_name='Полная ссылка', null=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'short_url'),
                name='unique_recipe_short_url'
            )
        ]
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        default_related_name = 'short_links'
    
    def __str__(self):
        return f'Короткая ссылка для рецепта {self.recipe} - {self.short_url}.'


class UserRecipeBaseModel(models.Model):
    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True


class Favourite(UserRecipeBaseModel):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favourites'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(UserRecipeBaseModel):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
