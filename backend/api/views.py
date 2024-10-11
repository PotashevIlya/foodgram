from http import HTTPStatus

from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import FoodgramUser, Subscription, Tag, Ingredient,Recipe
from .serializers import (AvatarSerializer,
                          ChangePasswordSerializer,
                          FoodgramUserCreateSerializer,
                          FoodgramUserReadSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeWriteSerializer,
                          RecipeReadSerializer
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
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer
    
    
        