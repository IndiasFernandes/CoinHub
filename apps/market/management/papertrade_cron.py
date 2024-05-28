import json

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.market.models import PaperTrade


class Command(BaseCommand):
    help = 'Setup periodic tasks for active paper trades'

    def handle(self, *args, **kwargs):
        for trade in PaperTrade.objects.filter(is_active=True):
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=trade.cron_timeframe,
                period=IntervalSchedule.SECONDS,
            )
            task, created = PeriodicTask.objects.get_or_create(
                interval=schedule,
                name=f'Paper Trade {trade.id} - {trade.name}',
                task='apps.market.run_paper_trading_task',
                args=json.dumps([trade.id]),
            )
            if not created:
                task.interval = schedule
                task.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully setup task for {trade.name}'))
