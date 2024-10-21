from http import HTTPStatus

from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response

from recipes.models import FoodgramUser, Recipe, RecipeShortURL


def create_object(request, id, serializer):
    recipe = get_object_or_404(Recipe, id=id)
    data = dict(user=request.user.id, recipe=recipe.id)
    serializer = serializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


def delete_object(request, id, model, model_name):
    user = FoodgramUser.objects.get(id=request.user.id)
    recipe = get_object_or_404(Recipe, id=id)
    instance = model.objects.filter(user=user, recipe=recipe)
    if instance.exists():
        instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(
        {'error': f'Этого рецепта не было в {model_name}'},
        status=HTTPStatus.BAD_REQUEST
    )


def get_full_url(short_url):
    try:
        recipe = get_object_or_404(RecipeShortURL, short_url=short_url)
    except RecipeShortURL.DoesNotExist:
        raise ValueError(
            'Рецепт не существует'
        )
    return recipe.full_url


def redirection(request, short_url):
    try:
        full_url = get_full_url(short_url)
        return redirect(full_url)
    except Exception as e:
        return Response({'errors': e})