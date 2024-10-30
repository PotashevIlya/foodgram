from http import HTTPStatus

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.models import (
    Favourite, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)
from .filters import IngredientsFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer, RecipeBriefSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    SubscriptionReadSerializer,
    TagSerializer
)
from .utils import create_object, delete_object, generate_shopping_list


class FoodgramUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

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
            user = request.user
            user.avatar = avatar
            user.save()
            return Response({'avatar': user.avatar.url}, status=HTTPStatus.OK)
        user = FoodgramUser.objects.get(id=request.user.id)
        user.avatar.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        methods=('POST', 'DELETE'),
        url_path=r'(?P<id>\d+)/subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def manage_subscription(self, request, id):
        data = dict(
            subscriber=request.user,
            author=get_object_or_404(FoodgramUser, id=id)
        )
        if request.method == 'POST':
            if data['subscriber'] == data['author']:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя самого'
                )
            if Subscription.objects.filter(**data).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя'
                )
            Subscription.objects.create(**data)
            return Response(
                SubscriptionReadSerializer(
                    data['author'],
                    context={'request': request},
                ).data,
                status=HTTPStatus.CREATED
            )
        subscription = Subscription.objects.filter(**data)
        if not subscription.exists():
            raise serializers.ValidationError(
                'Вы не были подписаны на этого пользователя'
            )
        subscription.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = FoodgramUser.objects.filter(
            authors__subscriber=request.user)
        serializer = SubscriptionReadSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=False,
        methods=('POST', 'DELETE'),
        url_path=r'(?P<id>\d+)/favorite',
        permission_classes=(IsAuthenticated,)
    )
    def manage_favorite(self, request, id):
        if request.method == 'POST':
            return create_object(
                request.user,
                id,
                RecipeBriefSerializer,
                Favourite,
                'избранном'
            )
        return delete_object(request.user, id, Favourite, 'избранном')

    @action(
        detail=False,
        methods=('POST', 'DELETE'),
        url_path=r'(?P<id>\d+)/shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def manage_shopping_cart(self, request, id):
        if request.method == 'POST':
            return create_object(
                request.user, id,
                RecipeBriefSerializer,
                ShoppingCart,
                'списке покупок'
            )
        return delete_object(request.user, id, ShoppingCart, 'списке покупок')

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_in_shopcart = RecipeIngredient.objects.filter(
            recipe__shoppingcart_recipes__user_id=request.user.id
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            ingredient_sum=Sum('amount')
        )
        recipes_in_shopcart = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            'recipe__name'
        )
        return FileResponse(
            generate_shopping_list(
                ingredients_in_shopcart,
                recipes_in_shopcart
            ),
            as_attachment=True,
            filename='shopping_list.txt'
        )
