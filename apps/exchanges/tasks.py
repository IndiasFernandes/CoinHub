import subprocess
from celery import shared_task
from apps.exchanges.utils.hyperliquid.bot import BotAccount

@shared_task
def record_exchange_info():
    bot_account = BotAccount()  # Initialize your bot account
    try:
        # Activate SSH
        activate_ssh_command = "sudo systemctl start ssh"
        subprocess.run(activate_ssh_command, shell=True, check=True)

        # Update exchange info
        bot_account.update_exchange_info()
        bot_account.print_info()

        # Capture the account value here if needed
        account_value = bot_account.get_account_value()
        print(f"Account Value: {account_value}")
    except subprocess.CalledProcessError as e:
        # Log the error if activation of SSH fails
        print(f"Error activating SSH: {e}")
    except Exception as e:
        # Log any other errors
        print(f"Error occurred: {e}")
