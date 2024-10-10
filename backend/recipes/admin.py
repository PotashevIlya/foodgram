from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription, Tag


class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar',)}),
    )


admin.site.register(FoodgramUser, FoodgramUserAdmin)
admin.site.register(Subscription)
admin.site.register(Tag)