from celery import shared_task
from apps.exchanges.utils.hyperliquid.bot import BotAccount
from celery import shared_task
import subprocess

from apps.market.models import PaperTrade


@shared_task
def record_exchange_info():
    try:
        # Specify the path to your script
        script_path = "/path/to/your/script.sh"

        # Execute the script
        result = subprocess.run(script_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")

@shared_task
def run_paper_trading_task(trade_id):
    trade = PaperTrade.objects.get(id=trade_id)
    if trade.is_active:
        execute_trade(trade)




    # bot_account = BotAccount()  # Initialize your bot account
    #
    #
    #
    # try:
    #     bot_account.update_exchange_info()
    #     bot_account.print_info()
    #
    #     # Capture the account value here if needed
    #     account_value = bot_account.get_account_value()
    #     print(f"Account Value: {account_value}")
    # except Exception as e:
    #     # Log the error
    #     print(f"Error occurred: {e}")
