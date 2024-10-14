from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription, Tag, Ingredient, Recipe, RecipeIngredient, Favourite, ShoppingCart


class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar',)}),
    )


admin.site.register(FoodgramUser, FoodgramUserAdmin)
admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)