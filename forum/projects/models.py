from django.db import models
from startups.models import Startup
from investors.models import Investor
from django.utils import timezone

from simple_history.models import HistoricalRecords


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        NEW = 'NEW'
        ACTIVE = 'ACTIVE'
        ON_HOLD = 'ON_HOLD'
        COMPLETED = 'COMPLETED'
        CANCELLED = 'CANCELLED'
        PENDING = 'PENDING'
        APPROVED = 'APPROVED'

    project_id = models.AutoField(primary_key=True)
    startup_id = models.ForeignKey(Startup, on_delete=models.CASCADE)
    status_id = models.CharField(max_length=10, choices=ProjectStatus.choices, default=ProjectStatus.NEW)
    title = models.CharField(max_length=200)
    business_plan = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True, help_text="Duration of the project in months")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    budget = models.IntegerField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'project'


class ProjectSubscription(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    investor_id = models.ForeignKey(Investor, on_delete=models.CASCADE)
    part = models.DecimalField(
        max_digits=5,  # Maximum number of digits (including decimals)
        decimal_places=2,  # Number of decimal places
        help_text="Investor's share in the project as a percentage"
    )

    class Meta:
        db_table = 'project_subscription'


class Industry(models.Model):
    industry_id = models.AutoField(primary_key=True)
    projects = models.ManyToManyField(Project, related_name='industry')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'industry'
