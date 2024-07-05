from django.db import models
from users.models import CustomUser
from django.utils import timezone


class Investor(models.Model):
    investor_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    investor_logo = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    contacts = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'investor'
