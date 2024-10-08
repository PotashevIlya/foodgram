import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import FoodgramUser


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FoodgramUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class FoodgramUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'avatar')


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)
    avatar_url = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True
    )

    def get_avatar_url(self, obj):
        return obj.avatar.url


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)
