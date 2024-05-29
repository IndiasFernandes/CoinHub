from django.core.management.base import BaseCommand
import time
from apps.exchanges.utils.hyperliquid.bot import BotAccount

class Command(BaseCommand):
    help = 'Records exchange information to the database every 10 minutes.'

    def handle(self, *args, **options):
        bot_account = BotAccount()  # Initialize your bot account

        while True:
            try:
                bot_account.update_exchange_info()
                bot_account.print_info()

            except Exception as e:
                self.stderr.write(f"Error occurred: {e}")
                # Optional: Log the error to a file or monitoring system
                time.sleep(60)  # Continue to wait and try again after 10 minutes

