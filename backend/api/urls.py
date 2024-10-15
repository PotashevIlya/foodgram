from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FoodgramUserViewSet, manage_subscribe, TagViewSet, IngredientViewSet, RecipeViewSet, 
    get_short_url, manage_favourite, manage_shopping_cart, download_shopping_cart)

router = DefaultRouter()
router.register(
    'users',
    FoodgramUserViewSet,
    basename='users'
)
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', manage_subscribe),
    path('recipes/<int:id>/get-link/', get_short_url),
    path('recipes/<int:id>/favorite/', manage_favourite, name='favourite'),
    path('recipes/<int:id>/shopping_cart/', manage_shopping_cart, name='shopping_cart'),
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
    path('', include(router.urls)),
]
