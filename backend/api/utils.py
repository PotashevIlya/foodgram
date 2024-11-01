import datetime
import io
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, RecipeIngredient
from rest_framework import serializers
from rest_framework.response import Response


def check_authentification(context):
    return (
        context
        and context['request'].user.is_authenticated
    )


def check_recipe_in_shopcart_or_favorites(context, model, obj):
    return (
        check_authentification(context)
        and model.objects.filter(
            user_id=context['request'].user.id,
            recipe=obj
        ).exists()
    )


def add_or_remove_recipe(request, id, model, serializer):
    if request.method == 'POST':
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт'
            )
        return Response(
            serializer(recipe).data,
            status=HTTPStatus.CREATED
        )
    get_object_or_404(model, user=request.user, recipe_id=id).delete()
    return Response(status=HTTPStatus.NO_CONTENT)


def create_ingredients_in_recipe(recipe, ingredients):
    ingredients_list = []
    for ingredient in ingredients:
        ingredient_id = ingredient.pop('id')
        ingredient_amount = ingredient.pop('amount')
        current_ingredient = Ingredient.objects.get(id=ingredient_id)
        ingredients_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient_amount
            )
        )
        RecipeIngredient.objects.bulk_create(ingredients_list)


def generate_shopping_list(products, recipes):
    products_in_shopcart = []
    recipes_in_shopcart = []
    for i, product in enumerate(products):
        name = product['ingredient__name'].capitalize()
        measurement_unit = product['ingredient__measurement_unit']
        amount = product['ingredient_sum']
        products_in_shopcart.append(
            f'{i+1}.{name} в количестве {amount} {measurement_unit}.'
        )
    for recipe in recipes:
        name = recipe['recipe__name'].capitalize()
        recipes_in_shopcart.append(
            f'- {name}'
        )
    return io.BytesIO(
        bytes(
            '\n'.join(
                [
                    f'Список покупок от {datetime.date.today().isoformat()}:',
                    'Продукты:',
                    *products_in_shopcart,
                    'Для рецептов:',
                    *recipes_in_shopcart
                ]
            ),
            encoding='utf-8'
        )
    )
