from django.db import models
from users.models import CustomUser
from django.utils import timezone
from django.core.exceptions import ValidationError


class StartupSize(models.Model):
    size_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    people_count_min = models.IntegerField(default=0)
    people_count_max = models.IntegerField()

    class Meta:
        db_table = 'startup_size'
        verbose_name = 'StartupSize'
        verbose_name_plural = 'StartupSizes'

    def __str__(self) -> str:
        return f"{self.name} ({self.people_count_min} - {self.people_count_max})"

    def clean(self):
        if self.people_count_min > self.people_count_max:
            raise ValidationError('people_count_min cannot be greater than people_count_max')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Startup(models.Model):
    startup_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="startups")
    name = models.CharField(max_length=200)
    size = models.ForeignKey(StartupSize, on_delete=models.CASCADE, blank=True, null=True, related_name="startup_sizes")
    location = models.CharField(max_length=200, blank=True, null=True)
    startup_logo = models.BinaryField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contacts = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'startup'
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'

    def __str__(self) -> str:
        return f"{self.startup_id} {self.name}"
