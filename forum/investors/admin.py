from django.contrib import admin

from .models import Investor


@admin.register(Investor)
class InvestorModelAdmin(admin.ModelAdmin):
    ...
