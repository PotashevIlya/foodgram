from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
            ('have_recipes', 'Есть рецепты'),
            ('have_subscriptions', 'Есть подписки'),
            ('have_subscribers', 'Есть подписчики')
        )

    def queryset(self, request, queryset):
        if self.value() == 'have_recipes':
            return queryset.exclude(recipes=None)
        if self.value() == 'have_subscriptions':
            return queryset.exclude(subscribers=None)
        if self.value() == 'have_subscribers':
            return queryset.exclude(authors=None)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'время готовки'
    parameter_name = 'cooking_time'
    fast = 30
    middle = 60
    fast_recipes = Recipe.objects.filter(cooking_time__lt=fast)
    middle_recipes = Recipe.objects.filter(cooking_time__range=(fast, middle))
    long_recipes = Recipe.objects.filter(cooking_time__gte=(middle))

    def lookups(self, request, model_admin):
        return (
            (
                'fast',
                f'Быстрее {self.fast} мин ({self.fast_recipes.count()})'
            ),
            (
                'middle',
                f'Быстрее {self.middle} мин ({self.middle_recipes.count()})'
            ),
            (
                'long',
                f'Долгие ({self.long_recipes.count()})'
            )
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return self.fast_recipes
        if self.value() == 'middle':
            return self.middle_recipes
        if self.value() == 'long':
            return self.long_recipes


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar', 'get_image', 'total_recipes',
         'total_subscribers', 'total_subscriptions')}),
    )
    search_fields = ('username', 'email',)
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'get_image', 'is_staff', 'total_recipes',
        'total_subscribers', 'total_subscriptions',
    )
    readonly_fields = (
        'get_image', 'total_recipes', 'total_subscribers',
        'total_subscriptions'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', FoodgramUserFilter
    )

    def total_recipes(self, user):
        if user.recipes.count() > 0:
            url = f'/admin/recipes/recipe/?author__id__exact={user.id}'
            return mark_safe(f'<a href="{url}">{user.recipes.count()}</a>')
        return user.recipes.count()

    def total_subscribers(self, user):
        return user.authors.count()

    def total_subscriptions(self, user):
        return user.subscribers.count()

    def get_image(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src={user.avatar.url} width="50" height="60">'
            )

    total_recipes.short_description = 'Всего рецептов'
    total_subscribers.short_description = 'Всего подписчиков'
    total_subscriptions.short_description = 'Всего подписок'
    get_image.short_description = 'Аватар'


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
    readonly_fields = (
        'total_in_favorites', 'get_image', 'get_tags', 'get_products'
    )

    def total_in_favorites(self, recipe):
        return recipe.favourite_recipes.count()

    def get_image(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src={recipe.image.url} width="50" height="60">'
            )

    def get_tags(self, recipe):
        tag_list = '\n'.join(
            [
                f'<li> {tag.name} </li>' for tag in Tag.objects.filter(
                    recipes=recipe
                )
            ]
        )
        return mark_safe(f'<ul> {tag_list} </ul>')

    def get_products(self, recipe):
        ingredients_list = '\n'.join(
            [
                f'<li>{i.name}</li>' for i in Ingredient.objects.filter(
                    recipes=recipe
                )
            ]
        )
        return mark_safe(f'<ul> {ingredients_list} </ul>')

    total_in_favorites.short_description = 'Всего в избранном'
    get_image.short_description = 'Изображение'
    get_tags.short_description = 'Категории'
    get_products.short_description = 'Продукты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)
