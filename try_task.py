# run_task.py
import os
import django
from celery import Celery

# Set up Django settings and initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings_production')
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
django.setup()

# Initialize Celery
app = Celery('CoinHub')

# Import the task
from apps.market.tasks import run_paper_trading_task

def main(trade_id):
    result = run_paper_trading_task.apply_async(args=[trade_id])
    print(f'Task ID: {result.id}')
    print('Task has been triggered. Check your Celery worker logs for execution details.')

if __name__ == '__main__':
    trade_id = 1  # Replace with the trade_id you want to test
    main(trade_id)
