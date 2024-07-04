from django.db import models
from users.models import CustomUser
from django.utils import timezone


class StartupSizes(models.Model):
    size_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    people_count_min = models.IntegerField(default=0)
    people_count_max = models.IntegerField()


class Startup(models.Model):
    startup_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    size = models.ForeignKey(StartupSizes, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    startup_logo = models.BinaryField()
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)
    contacts = models.JSONField(blank=True, null=True)
