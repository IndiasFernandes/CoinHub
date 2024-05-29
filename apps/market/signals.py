import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import PaperTrade

@receiver(post_save, sender=PaperTrade)
def create_or_update_paper_trade_task(sender, instance, created, **kwargs):
    task_name = f'PaperTrade_{instance.id}_task'
    print(f"SIGNAL - Attempting to create or update periodic task for PaperTrade {instance.id}")
    schedule, schedule_created = IntervalSchedule.objects.get_or_create(
        every=instance.cron_timeframe,
        period=IntervalSchedule.SECONDS,
    )

    if schedule_created:
        print(f"SIGNAL - Created new schedule: {schedule.id} for every {schedule.every} seconds")

    task, task_created = PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            'interval': schedule,
            'task': 'apps.market.tasks.run_paper_trading_task',
            'args': json.dumps([instance.id]),
            'enabled': instance.is_active  # Make sure to enable/disable based on the active status
        }
    )

    if task_created:
        print(f"SIGNAL - Created new periodic task {task.name}")
    else:
        print(f"SIGNAL - Updated existing periodic task {task.name}")

    if not task_created and task.interval != schedule:
        task.interval = schedule
        task.save()
        print(f"SIGNAL - Updated schedule for task {task.name} to {schedule.every} seconds")

@receiver(post_delete, sender=PaperTrade)
def delete_paper_trade_task(sender, instance, **kwargs):
    task_name = f'PaperTrade_{instance.id}_task'
    print(f"SIGNAL - Attempting to delete periodic task for PaperTrade {instance.id}")
    try:
        task = PeriodicTask.objects.get(name=task_name)
        task.delete()
        print(f"SIGNAL - Deleted periodic task {task.name}")
    except PeriodicTask.DoesNotExist:
        print(f"SIGNAL - Periodic task {task_name} not found for deletion")
