from django.core.management.base import BaseCommand
from django.utils import timezone
import time

from exchanges.models import ExchangeInfo
from exchanges.utils.hyperliquid.utils import BotAccount  # Import your BotAccount or equivalent

class Command(BaseCommand):
    help = 'Records exchange information to the database every 5 minutes.'

    def handle(self, *args, **options):
        bot_account = BotAccount()  # Initialize your bot account

        while True:
            self.stdout.write(self.style.SUCCESS(f'Recording exchange information at {timezone.now()}'))
            user_state = bot_account.user_state
            margin_summary = bot_account.margin_summary

            # Create a new ExchangeInfo record with the relevant data
            ExchangeInfo.objects.create(
                account_value=margin_summary.get("accountValue", 0),
                total_margin_used=margin_summary.get("totalMarginUsed", 0),
                total_net_position=margin_summary.get("totalNtlPos", 0),
                total_raw_usd=margin_summary.get("totalRawUsd", 0),
                withdrawable=user_state.get("withdrawable", 0),
            )

            # Sleep for 5 minutes (300 seconds) before the next record
            time.sleep(300)
