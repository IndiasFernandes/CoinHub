from celery import shared_task
from django.core.management import call_command

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_read_hyperliquid_command(self):
    try:
        call_command('read_hyperliquid')
    except Exception as e:
        self.retry(exc=e)


# from celery import shared_task
# from apps.exchanges.utils.hyperliquid.bot import BotAccount
# from celery import shared_task
# import subprocess
#
# from apps.market.models import PaperTrade
#
#
# @shared_task
# def record_exchange_info():
#     print("Starting the task execution...")
#
#     try:
#         # Specify the path to your script
#         script_path = "/path/to/your/script.sh"
#
#         # Execute the script
#         result = subprocess.run(script_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
#         print(output)
#     except subprocess.CalledProcessError as e:
#         print(f"Error executing script: {e}")
#
#
#     # Import the task
#     from apps.market.tasks import run_paper_trading_task
#
#     def main(trade_id):
#         print("Starting the task execution...")
#         try:
#             result = run_paper_trading_task.apply_async(args=[trade_id])
#             print(f'Task ID: {result.id}')
#             print('Task has been triggered. Check your Celery worker logs for execution details.')
#         except Exception as e:
#             print(f"An error occurred: {e}")
#
#     if __name__ == '__main__':
#         trade_id = 1  # Replace with the trade_id you want to test
#         main(trade_id)
#
#     # bot_account = BotAccount()  # Initialize your bot account
#     #
#     #
#     #
#     # try:
#     #     bot_account.update_exchange_info()
#     #     bot_account.print_info()
#     #
#     #     # Capture the account value here if needed
#     #     account_value = bot_account.get_account_value()
#     #     print(f"Account Value: {account_value}")
#     # except Exception as e:
#     #     # Log the error
#     #     print(f"Error occurred: {e}")
