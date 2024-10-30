from django.urls import path

from .views import redirection


urlpatterns = [
    path('<id>', redirection),
]
