from celery import shared_task
from CoinHub import settings
from apps.market.models import PaperTrade
from apps.market.utils.trading_functions import paper_trade_execute
import logging
import os

# Configure logging outside the task function, but ensure it only configures once
log_path = os.path.join(settings.BASE_DIR, 'logs', 'task_paper_log.log')
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_paper_trading_task(self, trade_id):
    logger.info('TASK TEST - Running Paper Trading Task')
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        logger.info(f"TASK TEST - PaperTrade object retrieved: {trade}")

        if trade.is_active:
            logger.info(f"TASK TEST - Executing paper trade for active trade: {trade_id}")
            paper_trade_execute(trade_id)
        else:
            logger.info(f"TASK TEST - Trade {trade_id} is not active.")
    except PaperTrade.DoesNotExist:
        logger.error(f"TASK TEST ERROR - No PaperTrade found for ID: {trade_id}")
    except Exception as e:
        logger.exception(f"TASK TEST ERROR - An error occurred:")  # This will log the full traceback
        self.retry(exc=e, countdown=60)
