from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Favourite, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)


class FoodgramUserFilter(admin.SimpleListFilter):
    title = 'детали'
    parameter_name = 'filter'

    def lookups(self, request, model_admin):
        return (
            ('recipes', 'Есть рецепты'),
            ('subscribers', 'Есть подписки'),
            ('authors', 'Есть подписчики')
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.exclude(**{f'{self.value()}': None})
        return queryset


class CookingTimeFilter(admin.SimpleListFilter):
    FAST = 30
    MIDDLE = 60
    COOKING_TIME_RANGES = {
        f'До {FAST} мин': (0, FAST),
        f'До {MIDDLE} мин': (FAST, MIDDLE),
        'Дольше': (MIDDLE, 10**10)
    }
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def get_filtered_recipes(self, queryset, param):
        return queryset.filter(cooking_time__range=param)

    def lookups(self, request, model_admin):
        string = '{name}({count})'
        return [
            (
                name,
                string.format(
                    name=name, count=self.get_filtered_recipes(
                        Recipe.objects.all(),
                        range
                    ).count()
                )
            )
            for name, range in self.COOKING_TIME_RANGES.items()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return self.get_filtered_recipes(
                queryset, self.COOKING_TIME_RANGES[f'{self.value()}']
            )
        return queryset


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar', 'get_image', 'total_recipes',
         'total_subscribers', 'total_subscriptions')}),
    )
    search_fields = ('username', 'email',)
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'get_avatar', 'is_staff', 'total_recipes',
        'total_subscribers', 'total_subscriptions',
    )
    readonly_fields = (
        'get_avatar', 'total_recipes', 'total_subscribers',
        'total_subscriptions'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', FoodgramUserFilter
    )

    @admin.display(description='Рецепты')
    def total_recipes(self, user):
        count = user.recipes.count()
        if count > 0:
            url = reverse('admin:recipes_recipe_changelist')
            return mark_safe(
                f'<a href="{url}?author__id__exact={user.id}">{count}</a>'
            )
        return count

    @admin.display(description='Подписчики')
    def total_subscribers(self, user):
        return user.followings.count()

    @admin.display(description='Подписки')
    def total_subscriptions(self, user):
        return user.subscribers.count()

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar(self, user):
        if user.avatar:
            return f'<img src={user.avatar.url} width="50" height="60">'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__username',)
    list_filter = ('tags', 'author', CookingTimeFilter)
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name', 'id', 'cooking_time', 'author', 'total_in_favorites',
        'get_image', 'get_tags', 'get_products'
    )
    readonly_fields = ('total_in_favorites', 'get_image')

    @admin.display(description='В избранном')
    def total_in_favorites(self, recipe):
        return recipe.favourite.count()

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, recipe):
        if recipe.image:
            return f'<img src={recipe.image.url} width="50" height="60">'

    @admin.display(description='Теги')
    @mark_safe
    def get_tags(self, recipe):
        return '</br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def get_products(self, recipe):
        product_string = ('{ingredient__name} в количестве {amount}'
                          '{ingredient__measurement_unit}.')
        ingredients_in_recipe = RecipeIngredient.objects.filter(
            recipe=recipe
        ).values(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        return '</br>'.join(
            product_string.format(**product)
            for product in ingredients_in_recipe
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Subscription)
class SubscpiptionAdmin(admin.ModelAdmin):
    search_fields = ('subscriber__username', 'author__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name', 'slug')


@admin.register(Favourite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(FavoriteAdmin):
    pass
