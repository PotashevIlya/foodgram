import base64

from django.core.files.base import ContentFile
from rest_framework import serializers, validators

from recipes.models import (MAX_EMAIL_LENGTH, MAX_PASSWORD_LENGTH,
                            MAX_RECIPE_NAME_LENGTH, MAX_USERNAME_LENGTH,
                            MIN_COOKING_TIME, Favourite, FoodgramUser,
                            Ingredient, Recipe, RecipeIngredient, ShoppingCart,
                            Subscription, Tag)
from recipes.validators import validate_username

from .utils import create_ingredients_in_recipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FoodgramUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, max_length=MAX_PASSWORD_LENGTH)
    username = serializers.CharField(max_length=MAX_USERNAME_LENGTH)
    first_name = serializers.CharField(max_length=MAX_USERNAME_LENGTH)
    last_name = serializers.CharField(max_length=MAX_USERNAME_LENGTH)
    email = serializers.CharField(max_length=MAX_EMAIL_LENGTH)

    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, username):
        if FoodgramUser.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        return validate_username(username)

    def validate_email(self, email):
        if FoodgramUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким e-mail уже существует'
            )
        return email


class FoodgramUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'avatar')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if len(self.context) == 0:
            data['is_subscribed'] = False
            return data
        if Subscription.objects.filter(
            subscriber_id=self.context['request'].user.id,
            following_id=instance.id
        ).exists():
            data['is_subscribed'] = True
            return data
        data['is_subscribed'] = False
        return data


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)
    avatar_url = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True
    )

    def get_avatar_url(self, obj):
        return obj.avatar.url


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, max_length=MAX_PASSWORD_LENGTH)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        current_user = self.initial_data['user']
        if not current_user.check_password(value):
            raise serializers.ValidationError(
                'Старый пароль неверен'
            )
        return value


class RecipeBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionReadSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count')
    is_subscribed = serializers.BooleanField(default=True)

    def get_recipes(self, obj):
        context = self.context.get('request')
        recipes_limit = context.query_params.get('recipes_limit')
        if recipes_limit:
            return RecipeBriefSerializer(
                obj.recipes.all()[:int(recipes_limit)],
                many=True
            ).data
        return RecipeBriefSerializer(obj.recipes.all(), many=True).data

    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes', 'recipes_count')


class SubscriptionWriteSerializer(serializers.ModelSerializer):
    subscriber = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all())
    following = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all())

    class Meta:
        model = Subscription
        fields = ('subscriber', 'following')
        validators = (validators.UniqueTogetherValidator(
            queryset=Subscription.objects.all(),
            fields=('subscriber', 'following'),
            message=('Вы уже подписаны на этого пользователя')
        ),
        )

    def validate(self, data):
        if data['subscriber'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя самого'
            )
        return data

    def to_representation(self, instance):
        return SubscriptionReadSerializer(
            instance.following,
            context={'request': self.context['request']}
        ).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = FoodgramUserReadSerializer()
    ingredients = RecipeIngredientsReadSerializer(
        many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        if len(self.context) == 0:
            return False
        return Favourite.objects.filter(
            user_id=self.context['request'].user.id,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if len(self.context) == 0:
            return False
        if self.context['request'].user.is_authenticated is False:
            return False
        return ShoppingCart.objects.filter(
            user_id=self.context['request'].user.id,
            recipe=obj
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientWriteSerializer(
        many=True, source='recipeingredients'
    )
    name = serializers.CharField(max_length=MAX_RECIPE_NAME_LENGTH)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        error_messages={
            'min_value': f'''Время приготовления не может
                            быть меньше {MIN_COOKING_TIME}'''
        }
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingredients(self, ingredients):
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов'
            )
        initial_ingredients = []
        for ingredient in ingredients:
            if Ingredient.objects.filter(
                id=ingredient['id']
            ).exists() is False:
                raise serializers.ValidationError(
                    'Ингредиента не существует'
                )
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Укажите ингредиент в количестве не меньше 1'
                )
            if ingredient in initial_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            initial_ingredients.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if len(tags) == 0:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег рецепта'
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег'
            )
        initial_tags = []
        for tag in tags:
            if tag in initial_tags:
                raise serializers.ValidationError(
                    'Теги не должны повторяться'
                )
            initial_tags.append(tag)
        return tags

    def validate(self, data):
        if 'recipeingredients' not in data:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов'
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без тегов'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_ingredients_in_recipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        create_ingredients_in_recipe(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer().to_representation(instance)


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')
        validators = (validators.UniqueTogetherValidator(
            queryset=Favourite.objects.all(),
            fields=('user', 'recipe'),
            message=('Этот рецепт уже есть в избранном')
        ),
        )

    def to_representation(self, instance):
        return RecipeBriefSerializer().to_representation(
            Recipe.objects.get(id=instance.recipe.id)
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = (validators.UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'),
            message=('Этот рецепт уже есть в списке покупок')
        ),
        )

    def to_representation(self, instance):
        return RecipeBriefSerializer().to_representation(
            Recipe.objects.get(id=instance.recipe.id)
        )
