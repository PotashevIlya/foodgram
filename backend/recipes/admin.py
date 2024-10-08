from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser


class FoodgramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Аватар', {'fields': ('avatar',)}),
    )


admin.site.register(FoodgramUser, FoodgramUserAdmin)
