from django.contrib import admin

from .models import CustomUser, PasswordResetModel


@admin.register(CustomUser)
class CustomUserModelAdmin(admin.ModelAdmin):
    ...


@admin.register(PasswordResetModel)
class PasswordResetAdminModel(admin.ModelAdmin):
    ...
