from http import HTTPStatus

from django.db.models import Sum
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import FoodgramUser, Subscription, Tag, Ingredient, Recipe, Favourite, ShoppingCart, RecipeIngredient
from .serializers import (AvatarSerializer,
                          ChangePasswordSerializer,
                          FoodgramUserCreateSerializer,
                          FoodgramUserReadSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeWriteSerializer,
                          RecipeReadSerializer,
                          FavouriteSerializer,
                          ShoppingCartSerializer
                          )


class FoodgramUserViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
    queryset = FoodgramUser.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return FoodgramUserReadSerializer
        return FoodgramUserCreateSerializer

    @action(
        detail=False,
        methods=('PUT', 'DELETE'),
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def manage_avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            avatar = serializer.validated_data['avatar']
            user = FoodgramUser.objects.get(id=request.user.id)
            user.avatar = avatar
            user.save()
            url = serializer.get_avatar_url(user)
            return Response({'avatar': url}, status=HTTPStatus.OK)
        user = FoodgramUser.objects.get(id=request.user.id)
        user.avatar.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = FoodgramUser.objects.get(id=request.user.id).subscriber
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = FoodgramUserReadSerializer(request.user)
        serializer.data['is_subscribed'] = False
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=('POST',)
    )
    def set_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid()
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        current_user = FoodgramUser.objects.get(id=request.user.id)
        if current_user.check_password(current_password):
            current_user.set_password(new_password)
            current_user.save()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response({'error': 'Старый пароль не правильный'})


@api_view(['POST', 'DELETE'])
def manage_subscribe(request, id):
    if request.method == 'POST':
        data = {}
        data['subscriber'] = request.user.id
        data['following'] = id
        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)
    if request.method == 'DELETE':
        subscriber = FoodgramUser.objects.get(id=request.user.id)
        following = FoodgramUser.objects.get(id=id)
        instance = Subscription.objects.filter(
            following=following, subscriber=subscriber)
        instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer


@api_view(['GET'])
def get_short_url(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    url = request.build_absolute_uri().replace('get-link/', '')
    return Response({'short-link': url})


@api_view(['POST', 'DELETE'])
def manage_favourite(request, id):
    if request.method == 'POST':
        data = {}
        data['user'] = request.user.id
        data['recipe'] = id
        serializer = FavouriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    if request.method == 'DELETE':
        user = FoodgramUser.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=id)
        instance = Favourite.objects.filter(
            user=user, recipe=recipe)
        instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


@api_view(['POST', 'DELETE'])
def manage_shopping_cart(request, id):
    if request.method == 'POST':
        data = {}
        data['user'] = request.user.id
        data['recipe'] = id
        serializer = ShoppingCartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    if request.method == 'DELETE':
        user = FoodgramUser.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=id)
        instance = ShoppingCart.objects.filter(
            user=user, recipe=recipe)
        instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    data = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                ingredient_sum=Sum('amount')
    )
    shopping_cart = []
    for ingredient in data:
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_sum']
        shopping_cart.append(
            f'- {name} в количестве {amount} {measurement_unit}\n')
    response = HttpResponse(shopping_cart, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    return response
