from django.contrib import admin

from .models import PasswordResetModel


@admin.register(PasswordResetModel)
class PasswordResetAdminModel(admin.ModelAdmin):
    ...
