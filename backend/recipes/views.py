from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirection(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return redirect(Recipe.get_absolute_url(request, id))
