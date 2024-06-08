from __future__ import absolute_import, unicode_literals
from CoinHub import settings
from celery.schedules import crontab
import os
from celery import Celery
from django.conf import settings
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')

app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Setup advanced logging
log_directory = os.path.join(settings.BASE_DIR, 'logs', 'celery.log')
if not os.path.exists(os.path.dirname(log_directory)):
    os.makedirs(os.path.dirname(log_directory))

handler = logging.FileHandler(log_directory)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app.conf.beat_schedule = {
    'run_read_hyperliquid_command_every_minute': {
        'task': 'apps.exchanges.tasks.run_read_hyperliquid_command',
        'schedule': 60.0,  # Execute every 60 seconds
    },
}
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.timezone = 'UTC'