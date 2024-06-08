from celery import shared_task

from CoinHub import settings
from apps.market.models import PaperTrade
from apps.market.utils.trading_functions import paper_trade_execute
import logging
import os

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_paper_trading_task(self, trade_id):
    # Configure logging
    log_path =  os.path.join(settings.BASE_DIR, 'logs', 'celery.log')
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    logging.info('TASK TEST - Running Paper Trading Task')
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        logging.info(f"TASK TEST - PaperTrade object retrieved: {trade}")

        if trade.is_active:
            logging.info(f"TASK TEST - Executing paper trade for active trade: {trade_id}")
            paper_trade_execute(trade_id)
        else:
            logging.info(f"TASK TEST - Trade {trade_id} is not active.")
    except PaperTrade.DoesNotExist:
        logging.error(f"TASK TEST ERROR - No PaperTrade found for ID: {trade_id}")
    except Exception as e:
        logging.error(f"TASK TEST ERROR - An error occurred: {str(e)}")
        self.retry(exc=e, countdown=60)
