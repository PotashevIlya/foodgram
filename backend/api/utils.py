import datetime

from recipes.models import Ingredient, RecipeIngredient


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
