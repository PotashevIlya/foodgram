from http import HTTPStatus

from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response

from recipes.models import (FoodgramUser, Ingredient, Recipe, RecipeIngredient,
                            RecipeShortURL)


def create_object(request, id, serializer):
    recipe = get_object_or_404(Recipe, id=id)
    data = dict(user=request.user.id, recipe=recipe.id)
    serializer = serializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


def delete_object(request, id, model, model_name):
    user = FoodgramUser.objects.get(id=request.user.id)
    recipe = get_object_or_404(Recipe, id=id)
    instance = model.objects.filter(user=user, recipe=recipe)
    if instance.exists():
        instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(
        {'error': f'Этого рецепта не было в {model_name}'},
        status=HTTPStatus.BAD_REQUEST
    )


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


def redirection(request, short_url):
    obj = get_object_or_404(RecipeShortURL, short_url=short_url)
    return redirect(obj.full_url)
