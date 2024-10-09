from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodgramUserViewSet, manage_subscribe

router = DefaultRouter()
router.register(
    'users',
    FoodgramUserViewSet,
    basename='users'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe', manage_subscribe),
    path('', include(router.urls)),
]
