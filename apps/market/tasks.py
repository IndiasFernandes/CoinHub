from celery import shared_task
import subprocess

from apps.market.models import PaperTrade
from apps.market.utils.trading_functions import paper_trade_execute


@shared_task
def run_paper_trading_task(trade_id):
    trade = PaperTrade.objects.get(id=trade_id)
    if trade.is_active:
        paper_trade_execute(trade)