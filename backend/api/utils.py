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
    current_date = datetime.date.today().isoformat()
    products_head = 'Продукты:'
    recipes_head = 'Рецепты:'
    products_in_shopcart = []
    recipes_in_shopcart = []
    for i, ingredient in enumerate(products):
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_sum']
        products_in_shopcart.append(
            f'{i+1}.{name.title()} в количестве {amount} {measurement_unit}.'
        )
    for recipe in recipes:
        name = recipe['recipe__name']
        recipes_in_shopcart.append(
            f'- {name.title()}'
        )
    result_content = '\n'.join(
        [
            current_date,
            products_head,
            *products_in_shopcart,
            recipes_head,
            *recipes_in_shopcart
        ]
    )
    shopping_list = io.BytesIO()
    shopping_list.write(bytes(result_content, encoding='utf-8'))
    shopping_list.seek(0)
    return shopping_list


# def redirection(request, short_url):
#     obj = get_object_or_404(RecipeShortURL, short_url=short_url)
#     return redirect(obj.full_url)
