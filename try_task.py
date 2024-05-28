# try_task.py
import os
import django
from celery import Celery

# Set up Django settings and initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings_production')
django.setup()

# Initialize Celery
app = Celery('CoinHub')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Import the task
from apps.market.tasks import run_paper_trading_task

def main(trade_id):
    print("Starting the task execution...")
    try:
        result = run_paper_trading_task.apply_async(args=[trade_id])
        print(f'Task ID: {result.id}')
        print('Task has been triggered. Check your Celery worker logs for execution details.')
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    trade_id = 1  # Replace with the trade_id you want to test
    main(trade_id)
