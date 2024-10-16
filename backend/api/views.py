from http import HTTPStatus


from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import FoodgramUser, Subscription, Tag, Ingredient, Recipe, Favourite, ShoppingCart, RecipeIngredient
from .serializers import (AvatarSerializer,
                          ChangePasswordSerializer,
                          FoodgramUserCreateSerializer,
                          FoodgramUserReadSerializer,
                          SubscriptionReadSerializer,
                          SubscriptionWriteSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeWriteSerializer,
                          RecipeReadSerializer,
                          FavouriteSerializer,
                          ShoppingCartSerializer
                          )
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientsFilter, RecipeFilter
from .pagination import CustomPagination


class FoodgramUserViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
    queryset = FoodgramUser.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

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
        request.data['user'] = FoodgramUser.objects.get(id=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            current_user = FoodgramUser.objects.get(id=request.user.id)
            current_user.set_password(
                serializer.validated_data['new_password'])
            current_user.save()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


class MySubscriptionsViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    serializer_class = SubscriptionReadSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return FoodgramUser.objects.filter(
            following__subscriber=self.request.user)


@api_view(['POST', 'DELETE'])
def manage_subscribe(request, id):
    if request.method == 'POST':
        following = get_object_or_404(FoodgramUser, id=id)
        data = {}
        data['subscriber'] = request.user.id
        data['following'] = id
        serializer = SubscriptionWriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    if request.method == 'DELETE':
        following = get_object_or_404(FoodgramUser, id=id)
        subscriber = FoodgramUser.objects.get(id=request.user.id)
        instance = Subscription.objects.filter(
            following=following, subscriber=subscriber)
        if instance.exists():
            instance.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
    return Response({'error': 'Нельзя оптисаться от пользователя, на которого вы не были подписаны'}, status=HTTPStatus.BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
    


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_short_url(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    url = request.build_absolute_uri().replace('get-link/', '')
    return Response({'short-link': url})


@api_view(['POST', 'DELETE'])
def manage_favourite(request, id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=id)
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
        recipe = get_object_or_404(Recipe, id=id)
        instance = Favourite.objects.filter(
            user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response({'error': 'Нельзя удалить из избранного рецепт, которого там нет'}, status=HTTPStatus.BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def manage_shopping_cart(request, id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=id)
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
        recipe = get_object_or_404(Recipe, id=id)
        instance = ShoppingCart.objects.filter(
            user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response({'error': 'Нельзя удалить из списка покупок рецепт, которого там нет'}, status=HTTPStatus.BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    data = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user_id=request.user.id).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                ingredient_sum=Sum('amount')
    )
    print(data)
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
