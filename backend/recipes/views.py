from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from .models import Recipe


def redirection(request, id):
    if not Recipe.objects.filter(id=id).exists():
        raise ValidationError(
            f'Рецепта не существует, id - {id}'
        )
    return redirect(request.build_absolute_uri(f'/recipes/{id}'))
