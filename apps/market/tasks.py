from celery import shared_task
import logging
from apps.market.models import PaperTrade
from apps.market.utils.trading_functions import paper_trade_execute

logger = logging.getLogger('celery')

@shared_task(bind=True, max_retries=3, soft_time_limit=60)
def run_paper_trading_task(self, trade_id):
    logger.info('Running Paper Trading Task')
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        logger.info(f"PaperTrade object retrieved: {trade}")

        if trade.is_active:
            logger.info(f"Executing paper trade for active trade: {trade_id}")
            paper_trade_execute(trade_id)
        else:
            logger.info(f"Trade {trade_id} is not active.")
    except PaperTrade.DoesNotExist:
        logger.error(f"No PaperTrade found for ID: {trade_id}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        self.retry(exc=e, countdown=60)
