import json

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import PaperTrade

@receiver(post_save, sender=PaperTrade)
def create_or_update_paper_trade_task(sender, instance, created, **kwargs):
    task_name = f'PaperTrade_{instance.id}_task'
    schedule, schedule_created = IntervalSchedule.objects.get_or_create(
        every=instance.cron_timeframe,
        period=IntervalSchedule.SECONDS,
    )

    task, task_created = PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            'interval': schedule,
            'task': 'apps.market.tasks.run_paper_trading_task',
            'args': json.dumps([instance.id]),
            'enabled': instance.is_active  # Make sure to enable/disable based on the active status
        }
    )

    if not task_created and task.interval != schedule:
        task.interval = schedule
        task.save()

@receiver(post_delete, sender=PaperTrade)
def delete_paper_trade_task(sender, instance, **kwargs):
    task_name = f'PaperTrade_{instance.id}_task'
    try:
        task = PeriodicTask.objects.get(name=task_name)
        task.delete()
    except PeriodicTask.DoesNotExist:
        pass
