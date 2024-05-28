import json
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.market.models import PaperTrade

class Command(BaseCommand):
    help = 'Setup and activate periodic tasks for active paper trades'

    def handle(self, *args, **kwargs):
        # Fetch all active trades
        active_trades = PaperTrade.objects.filter(is_active=True)

        for trade in active_trades:
            # Ensure each trade has a corresponding interval schedule in seconds
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=trade.cron_timeframe,
                period=IntervalSchedule.SECONDS,
            )
            # Create or update the periodic task
            task, created = PeriodicTask.objects.get_or_create(
                interval=schedule,
                name=f'Paper Trade {trade.id} - {trade.name}',
                task='apps.market.tasks.run_paper_trading_task',
                defaults={'args': json.dumps([trade.id])}
            )
            if not created:
                if task.interval != schedule:
                    task.interval = schedule
                    task.save()
                if not task.enabled:
                    task.enabled = True
                    task.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully setup or updated task for {trade.name}'))

        # Disable tasks for any inactive trades
        inactive_trades = PaperTrade.objects.filter(is_active=False)
        for trade in inactive_trades:
            try:
                task = PeriodicTask.objects.get(name=f'Paper Trade {trade.id} - {trade.name}',
                                                task='apps.market.tasks.run_paper_trading_task')
                if task.enabled:
                    task.enabled = False
                    task.save()
                    self.stdout.write(self.style.SUCCESS(f'Disabled task for {trade.name}'))
            except PeriodicTask.DoesNotExist:
                continue
