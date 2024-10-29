from http import HTTPStatus

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
    for ingredient in ingredients:
        ingredient_id = ingredient.pop('id')
        ingredient_amount = ingredient.pop('amount')
        current_ingredient = Ingredient.objects.get(id=ingredient_id)
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=current_ingredient,
            amount=ingredient_amount
        )


# def redirection(request, short_url):
#     obj = get_object_or_404(RecipeShortURL, short_url=short_url)
#     return redirect(obj.full_url)
