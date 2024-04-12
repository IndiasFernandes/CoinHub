# tasks.py in your bots app
from django.utils import timezone
from ..exchanges.utils.hyperliquid.bot import BotAccount
from celery import shared_task
from .models import Bot
import time


@shared_task
def update_bot_status_and_values(bot_id):
    bot = Bot.objects.get(id=bot_id)
    if bot.is_active:
        bot.is_active = not bot.is_active
        bot = BotAccount()
        bot.update_exchange_info()
        bot.updated_at = timezone.now()
        print(f"Bot updated at {bot.updated_at}")
        time.sleep(5)

@shared_task(bind=True)
def run_bot_loop(self, bot_id, sleep_time):
    try:
        bot = Bot.objects.get(id=bot_id)
    except Bot.DoesNotExist:
        return

    # Store the current task id in the bot instance
    bot.task_id = self.request.id
    bot.save(update_fields=['task_id'])
    bot_account = BotAccount()
    bot_account.test_functions()
    while bot.is_active:

        # Your bot's operational logic here
        print(f"Running bot loop for {bot.name}")
        time.sleep(sleep_time)  # Adjust the sleep time as needed

        # Refresh the bot instance from the database to get the latest status
        bot_account.update_exchange_info()
        bot_account.updated_at = timezone.now()

    # Clear the task_id once the loop is done
    bot.task_id = ''
    bot.save(update_fields=['task_id'])