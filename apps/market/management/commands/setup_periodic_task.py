import json
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db import IntegrityError

from apps.market.models import PaperShave

class Command(BaseCommand):
    help = 'Setup and activate periodic tasks for active paper trades'

    def handle(self, *args, **kwargs):
        # Handle all active trades
        self.setup_active_trades()

        # Disable tasks for any inactive trades
        self.disable_inactive_trades()

    def setup_active_trades(self):
        active_trades = PaperTrade.objects.filter(is_active=True)
        for trade in active_trades:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=trade.cron_timeframe,
                period=IntervalSchedule.SECONDS,
            )
            try:
                task, created = PeriodicTask.objects.update_or_create(
                    name=f'Paper Trade {trade.id} - {trade.name}',
                    defaults={
                        'interval': schedule,
                        'task': 'apps.market.tasks.run_paper_trading_task',
                        'args': json.dumps([trade.id]),
                        'enabled': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created task for {trade.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated task for {trade.name}'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating or updating task for {trade.name}: {str(e)}'))

    def disable_inactive_trades(self):
        inactive_trades = PaperTrade.objects.filter(is_active=False)
        for trade in inactive_trades:
            try:
                task = PeriodicTask.objects.get(
                    name=f'Paper Trade {trade.id} - {trade.name}',
                    task='apps.market.tasks.run_paper_trading_task'
                )
                if task.enabled:
                    task.enabled = False
                    task.save()
                    self.stdout.write(self.style.SUCCESS(f'Disabled task for {trade.name}'))
            except PeriodicTask.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'No task found for inactive trade {trade.name}'))
