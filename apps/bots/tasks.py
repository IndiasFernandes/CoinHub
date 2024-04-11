# tasks.py in your bots app
from datetime import time
from celery import shared_task
from .models import Bot
from django.utils import timezone
from ..exchanges.utils.hyperliquid.utils import BotAccount


@shared_task
def update_bot_status_and_values(bot_id):
    bot = Bot.objects.get(id=bot_id)
    if bot.is_active:
        bot = BotAccount()
        bot.update_exchange_info()
        bot.updated_at = timezone.now()
        print(f"Bot {bot.name} updated at {bot.updated_at}")
        time.sleep(5)
