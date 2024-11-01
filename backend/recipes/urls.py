from django.urls import path

from .views import redirection

urlpatterns = [
    path('<int:id>', redirection),
]
