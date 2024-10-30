from http import HTTPStatus
import datetime
import io

from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient


def create_object(user, recipe_id, serializer, model, model_name):
    data = dict(user=user, recipe=get_object_or_404(Recipe, id=recipe_id))
    if model.objects.filter(**data).exists():
        raise serializers.ValidationError(
            f'Этот рецепт уже есть в {model_name}'
        )
    model.objects.create(**data)
    return Response(
        serializer(data['recipe']).data,
        status=HTTPStatus.CREATED
    )


def delete_object(user, recipe_id, model, model_name):
    data = dict(user=user, recipe=get_object_or_404(Recipe, id=recipe_id))
    object = model.objects.filter(**data)
    if not object.exists():
        raise serializers.ValidationError(
            f'Этого рецепта нет в {model_name}'
        )
    object.delete()
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


# def redirection(request, short_url):
#     obj = get_object_or_404(RecipeShortURL, short_url=short_url)
#     return redirect(obj.full_url)
