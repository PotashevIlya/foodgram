from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodgramUserViewSet, manage_subscribe, TagViewSet, IngredientViewSet

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

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe', manage_subscribe),
    path('', include(router.urls)),
]
