from django.db import models
from startups.models import Startup
from investors.models import Investor
from django.utils import timezone

from simple_history.models import HistoricalRecords


class ProjectStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'project_status'
        verbose_name = 'ProjectStatus'
        verbose_name_plural = 'ProjectStatuses'
    
    def __str__(self):
        return self.title


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
    budget = models.IntegerField(blank=True, null=True)
    history = HistoricalRecords()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self) -> str:
        return f"{self.project_id} {self.title}"


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
