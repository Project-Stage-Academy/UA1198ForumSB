from django.contrib import admin

from .models import Project, ProjectSubscription, Industry


@admin.register(Project)
class ProjectModelAdmin(admin.ModelAdmin):
    ...


@admin.register(ProjectSubscription)
class ProjectSubscriptionModelAdmin(admin.ModelAdmin):
    ...


@admin.register(Industry)
class IndustryModelAdmin(admin.ModelAdmin):
    ...
