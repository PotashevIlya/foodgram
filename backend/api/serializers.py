from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.constants import (
    MAX_RECIPE_NAME_LENGTH, MIN_COOKING_TIME, MIN_AMOUNT
)
from recipes.models import (
    Favourite, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)
from .validators import validate_ingredients_or_tags
from rest_framework import serializers

from .utils import (
    get_serializer_method_field_value,
    create_ingredients_in_recipe
)


class NeverEmptyBase64ImageField(Base64ImageField):
    EMPTY_VALUES = ()


class FoodgramUserReadSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = (*UserSerializer.Meta.fields, 'avatar', 'is_subscribed')

    def get_is_subscribed(self, author):
        return get_serializer_method_field_value(
            self.context, Subscription, author, 'subscriber', 'author'
        )


class AvatarSerializer(serializers.Serializer):
    avatar = NeverEmptyBase64ImageField()


class RecipeBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionReadSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count')
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = FoodgramUser
        fields = (
            *FoodgramUserReadSerializer.Meta.fields, 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        return RecipeBriefSerializer(
            obj.recipes.all()[:int(
                self.context.get(
                    'request'
                ).query_params.get(
                    'recipes_limit',
                    10**10
                ))],
            many=True
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
        exclude = ('recipe', 'ingredient')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


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
        exclude = ('pub_date',)
        read_only_fields = ('id', 'tags', 'author', 'ingredients',
                            'is_favorited', 'is_in_shopping_cart',
                            'name', 'image', 'text', 'cooking_time'
                            )

    def get_is_favorited(self, recipe):
        return get_serializer_method_field_value(
            self.context, Favourite, recipe, 'user_id', 'recipe'
        )

    def get_is_in_shopping_cart(self, recipe):
        return get_serializer_method_field_value(
            self.context, ShoppingCart, recipe, 'user_id', 'recipe'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = NeverEmptyBase64ImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)
    name = serializers.CharField(max_length=MAX_RECIPE_NAME_LENGTH)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        error_messages={
            'min_value': f'Укажите время больше {MIN_COOKING_TIME} м.'
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        all_id = [ingredient['id'] for ingredient in ingredients]
        validate_ingredients_or_tags(all_id, Ingredient, 'ingredients')
        small_amount = [
            ingredient['id']
            for ingredient in ingredients if ingredient['amount'] < MIN_AMOUNT
        ]
        if small_amount:
            raise serializers.ValidationError(
                {
                    'id': small_amount,
                    'error': f'Мера меньше допустимой. Минимум - {MIN_AMOUNT}'
                }
            )
        return ingredients

    def validate_tags(self, tags):
        all_id = [tag.id for tag in tags]
        validate_ingredients_or_tags(all_id, Tag, 'tags')
        return tags

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов'
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без тегов'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        create_ingredients_in_recipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        create_ingredients_in_recipe(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context['request']}
        ).data
