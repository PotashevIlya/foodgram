from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodgramUserViewSet

router = DefaultRouter()
router.register(
    'users',
    FoodgramUserViewSet,
    basename='users'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
