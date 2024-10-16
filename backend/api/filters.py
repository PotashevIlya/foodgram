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

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favourites__user=self.request.user)
        return queryset
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset
    
    class Meta:
        model = Recipe
        fields = ('author','tags', 'is_favorited', 'is_in_shopping_cart')