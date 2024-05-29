from celery import shared_task
from apps.market.models import PaperTrade
from apps.market.utils.trading_functions import paper_trade_execute

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_paper_trading_task(self, trade_id):
    print('TASK TEST - Running Paper Trading Task')
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        print(f"TASK TEST - PaperTrade object retrieved: {trade}")

        if trade.is_active:
            print(f"TASK TEST - Executing paper trade for active trade: {trade_id}")
            paper_trade_execute(trade_id)
        else:
            print(f"TASK TEST - Trade {trade_id} is not active.")
    except PaperTrade.DoesNotExist:
        print(f"TASK TEST ERROR - No PaperTrade found for ID: {trade_id}")
    except Exception as e:
        print(f"TASK TEST ERROR - An error occurred: {str(e)}")
        self.retry(exc=e, countdown=60)
