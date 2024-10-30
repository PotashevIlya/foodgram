from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (
    Favourite, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)

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

    def total_recipes(self, user):
        return user.recipes.count()

    def total_subscribers(self, user):
        return user.authors.count()

    def total_subscriptions(self, user):
        return user.subscribers.count()
    

    def get_image(self, user):
        if user.avatar:
            return mark_safe(f'<img src={user.avatar.url} width="50" height="60">')

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
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'total_in_favorites')
    readonly_fields = ('total_in_favorites',)

    def total_in_favorites(self, recipe):
        return recipe.favourite_recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)
