from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')

app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Define the periodic task schedule
app.conf.beat_schedule = {
    'record_exchange_info_every_10_minutes': {
        'task': 'exchanges.tasks.record_exchange_info',
        'schedule': crontab(minute='*/10'),  # Execute every 10 minutes
    },
}
