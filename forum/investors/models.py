from django.db import models
from users.models import CustomUser
from django.utils import timezone


class Investor(models.Model):
    investor_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="investors")
    investor_logo = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    contacts = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'investor'
        verbose_name = 'Investor'
        verbose_name_plural = 'Investors'
