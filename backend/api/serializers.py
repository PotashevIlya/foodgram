import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import FoodgramUser, Subscription, Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag


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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if len(self.context) == 0:
            data['is_subscribed'] = False
            return data
        if Subscription.objects.filter(subscriber=self.context['request'].user, following=instance).exists():
            data['is_subscribed'] = True
            return data
        data['is_subscribed'] = False
        return data


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


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('subscriber', 'following')

    def create(self, validated_data):
        subscription = Subscription.objects.create(
            following=validated_data['following'], subscriber=validated_data['subscriber'])
        return subscription

    def to_representation(self, instance):
        data = FoodgramUserReadSerializer().to_representation(
            FoodgramUser.objects.get(id=instance.following_id))
        data['is_subscribed'] = True
        return data


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        exclude = ('recipe', 'ingredient')


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredients = RecipeIngredientReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author','ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        author_data = FoodgramUserReadSerializer().to_representation(
            FoodgramUser.objects.get(id=self.context['request'].user.id))
        data['author'] = author_data
        # recipe_ingredient_data = RecipeIngredientReadSerializer(
        # ).to_representation(RecipeIngredient.objects.get(id=7))
        # print(recipe_ingredient_data)
        # data['ingredients'] = recipe_ingredient_data
        return data


class RecipeIngredientWriteSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    class Meta:
        model = RecipeIngredient
        exclude = ('recipe', 'ingredient')



class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = serializers.ListField(write_only=True)
    tags = TagSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def to_internal_value(self, data):
        tags_id = data.pop('tags')
        formatted_tags_data = []
        for tag_id in tags_id:
            temp = dict(id=tag_id)
            formatted_tags_data.append(temp)
        data['tags'] = formatted_tags_data
        return super().to_internal_value(data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag_id in tags:
            current_tag = Tag.objects.get(**tag_id)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            ingredient_id = ingredient.pop('id')
            ingredient_amount = ingredient.pop('amount')
            current_ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=ingredient_amount)
        return recipe

    def to_representation(self, instance):
        data = super().to_representation(instance)
        author_data = FoodgramUserReadSerializer().to_representation(
            FoodgramUser.objects.get(id=self.context['request'].user.id))
        data['author'] = author_data
        # recipe_ingredient_data = RecipeIngredientReadSerializer(
        # ).to_representation(RecipeIngredient.objects.get(id=7))
        # data['ingredients'] = recipe_ingredient_data
        return data

