from django.db import models
from startups.models import Startup
from investors.models import Investor
from django.utils import timezone


class ProjectStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'project_status'
        verbose_name = 'ProjectStatus'
        verbose_name_plural = 'ProjectStatuses'


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    startup = models.OneToOneField(Startup, on_delete=models.CASCADE, related_name="project")
    status = models.ForeignKey(ProjectStatus, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    business_plan = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration of the project in months")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    budget = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class ProjectSubscription(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_subscriptions")
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="project_subscriptions")
    part = models.PositiveIntegerField()

    class Meta:
        db_table = 'project_subscription'
        verbose_name = 'ProjectSubscription'
        verbose_name_plural = 'ProjectSubscriptions'


class Industry(models.Model):
    industry_id = models.AutoField(primary_key=True)
    projects = models.ManyToManyField(Project, related_name='industries')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'industry'
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'

