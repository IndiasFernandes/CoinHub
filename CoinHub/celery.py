from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings_production')

app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run_read_hyperliquid_command_every_minute': {
        'task': 'apps.exchanges.tasks.run_read_hyperliquid_command',
        'schedule': 60.0,  # Execute every 60 seconds
    },
}
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.timezone = 'UTC'
