from django.core.management.base import BaseCommand
import time
from apps.exchanges.utils.utils import BotAccount  # Import your BotAccount or equivalent

class Command(BaseCommand):
    help = 'Records exchange information to the database every 5 minutes.'

    def handle(self, *args, **options):
        bot_account = BotAccount()  # Initialize your bot account

        while True:
            bot_account.update_exchange_info()
            bot_account.print_info()


            # Sleep for half minute (30 seconds) before the next record
            time.sleep(5)
