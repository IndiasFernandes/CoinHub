from celery import shared_task
from apps.exchanges.utils.hyperliquid.bot import BotAccount

@shared_task
def record_exchange_info():
    bot_account = BotAccount()  # Initialize your bot account
    try:
        bot_account.update_exchange_info()
        bot_account.print_info()

        # Capture the account value here if needed
        account_value = bot_account.get_account_value()
        print(f"Account Value: {account_value}")
    except Exception as e:
        # Log the error
        print(f"Error occurred: {e}")
