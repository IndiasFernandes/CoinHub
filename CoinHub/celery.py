from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')

app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Setup basic logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler('celery.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app.conf.beat_schedule = {
    'run_read_hyperliquid_command_every_minute': {
        'task': 'apps.exchanges.tasks.run_read_hyperliquid_command',
        'schedule': crontab(),  # Executes every minute
    },
}
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
app.conf.timezone = 'UTC'
