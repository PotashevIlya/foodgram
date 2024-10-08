from http import HTTPStatus

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import FoodgramUser
from .serializers import (AvatarSerializer,
                          ChangePasswordSerializer,
                          FoodgramUserCreateSerializer,
                          FoodgramUserReadSerializer
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
    def me(self, request):
        serializer = FoodgramUserReadSerializer(request.user)
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
