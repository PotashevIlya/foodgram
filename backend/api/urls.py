from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FoodgramUserViewSet, IngredientViewSet, RecipeViewSet,
    TagViewSet
)

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
    path('', include(router.urls)),
]
