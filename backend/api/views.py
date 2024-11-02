from http import HTTPStatus

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favourite, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import IngredientsFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer,
    RecipeBriefSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscriptionReadSerializer,
    TagSerializer
)
from .utils import add_or_remove_recipe, generate_shopping_list


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
        request.user.avatar.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        methods=('POST', 'DELETE'),
        url_path=r'(?P<id>\d+)/subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def manage_subscription(self, request, id):
        subscriber = request.user
        author = get_object_or_404(FoodgramUser, id=id)
        if request.method == 'POST':
            if subscriber == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя самого'
                )
            subcription, created = Subscription.objects.get_or_create(
                subscriber=subscriber,
                author=author
            )
            if not created:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя'
                )
            return Response(
                SubscriptionReadSerializer(
                    author,
                    context={'request': request},
                ).data,
                status=HTTPStatus.CREATED
            )
        get_object_or_404(
            Subscription,
            author=author,
            subscriber=subscriber
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscriptionReadSerializer(
                self.paginate_queryset(FoodgramUser.objects.filter(
                    followings__subscriber=request.user
                )),
                context={'request': request},
                many=True
            ).data
        )


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
        return add_or_remove_recipe(
            request, id, Favourite, RecipeBriefSerializer
        )

    @action(
        detail=False,
        methods=('POST', 'DELETE'),
        url_path=r'(?P<id>\d+)/shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def manage_shopping_cart(self, request, id):
        return add_or_remove_recipe(
            request, id, ShoppingCart, RecipeBriefSerializer
        )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_in_shopcart = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user_id=request.user.id
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

    @action(
        detail=False,
        url_path=r'(?P<id>\d+)/get-link',
        permission_classes=(AllowAny,)
    )
    def get_short_link(view, request, **kwargs):
        if not Recipe.objects.filter(id=kwargs['id']).exists():
            raise serializers.ValidationError(
                'Рецепта не существует'
            )
        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{kwargs["id"]}')})
