from os import environ

from django.conf import settings
from celery import Celery
from celery.schedules import crontab

from .tasks import password_reset_ttl_task


environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

app = Celery('forum', include=['forum.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/2'),
        password_reset_ttl_task.s(),
    )
