from django.contrib import admin

from .models import StartupSize, Startup


@admin.register(StartupSize)
class StartupSizeModelAdmin(admin.ModelAdmin):
    ...


@admin.register(Startup)
class StartupModelAdmin(admin.ModelAdmin):
    ...
