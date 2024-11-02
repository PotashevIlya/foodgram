import datetime
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, RecipeIngredient
from rest_framework import serializers
from rest_framework.response import Response


def get_serializer_method_field_value(
        context, model, obj, field_1, field_2
):
    return (
        context
        and context['request'].user.is_authenticated
        and model.objects.filter(
            **{f'{field_1}': context['request'].user.id, f'{field_2}': obj}
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
    ingredients_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=ingredient.pop('id')),
            amount=ingredient.pop('amount')
        ) for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(
        ingredients_list, ignore_conflicts=True
    )


def generate_shopping_list(products, recipes):
    product_string = ('{i}.{ingredient__name} в количестве {ingredient_sum}'
                      '{ingredient__measurement_unit}.')
    recipe_string = '- {recipe__name}'
    products_in_shopcart = [
        product_string.format(i=i, **product)
        for i, product in enumerate(products, start=1)
    ]
    recipes_in_shopcart = [
        recipe_string.format(**recipe) for recipe in recipes
    ]
    return '\n'.join(
        [
            f'Список покупок от {datetime.date.today().isoformat()}:',
            'Продукты:',
            *products_in_shopcart,
            'Для рецептов:',
            *recipes_in_shopcart
        ]
    )
