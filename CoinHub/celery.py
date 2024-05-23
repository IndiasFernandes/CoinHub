from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings_production')

app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Define the periodic task schedule
app.conf.beat_schedule = {
    'record_exchange_info_every_30_seconds': {
        'task': 'apps.exchanges.tasks.record_exchange_info',
        'schedule': 30.0,  # Execute every 30 seconds
    },
}
app.conf.timezone = 'UTC'
