from django_filters import rest_framework as filter

from recipes.models import Ingredient, Recipe


class IngredientsFilter(filter.FilterSet):

    name = filter.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filter.FilterSet):
    author = filter.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filter.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filter.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, recipes, name, value):
        if value:
            return recipes.filter(
                favourite_recipes__user_id=self.request.user.id
            )
        return recipes

    def get_is_in_shopping_cart(self, recipes, name, value):
        if value:
            return recipes.filter(
                shoppingcart_recipes__user_id=self.request.user.id
            )
        return recipes

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
