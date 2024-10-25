from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Favourite, FoodgramUser, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart,
                     Subscription, Tag)


class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar',)}),
    )
    search_fields = ('username', 'email',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'total_in_favorites')
    readonly_fields = ('total_in_favorites',)

    def total_in_favorites(self, obj):
        return Favourite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(FoodgramUser, FoodgramUserAdmin)
admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)
