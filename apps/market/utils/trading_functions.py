from datetime import timezone, timedelta

import ccxt
from django.shortcuts import get_object_or_404

from apps.exchanges.models import Exchange
from apps.exchanges.utils.hyperliquid.download_data import download_data
from apps.market.backtesting.backtest_utils import run_backtest
from apps.market.models import PaperTrade, MarketData


def paper_trade_execute(trade_id):
    try:
        trade = PaperTrade.objects.get(id=trade_id)
    except PaperTrade.DoesNotExist:
        print("Trade not found.")
        return  # Optionally log this error

    if not trade.is_active:
        print("Trade is not active.")
        return  # Trade is not active, do nothing

    # Fetch exchange details from Exchange model using id_char
    exchange = get_object_or_404(Exchange, id_char=trade.exchange.name)
    key = exchange.api_key
    secret = exchange.api_secret

    # Initialize the exchange instance, assuming CCXT usage
    exchange_class = getattr(ccxt, exchange.name)  # Ensure the name matches the CCXT identifier
    exchange_instance = exchange_class({
        'apiKey': key,
        'secret': secret,
        'timeout': 30000,
        'enableRateLimit': True,
    })

    # Define the timeframe for data to be fetched
    end_date = timezone.now()
    start_date = end_date - timedelta(days=trade.lookback_period)
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    # Download data using the utility function
    df = download_data([trade.coin.symbol], [trade.timeframe], start_date_str, end_date_str, exchange_instance)
    print("Downloaded data.")

    # Run backtest using the utility function
    st, price = run_backtest(trade.coin.symbol, df, trade.timeframe, trade.initial_balance, trade.commission, trade.openbrowser)
    print("Backtest results: st:", st, "price:", price)

    # Create or update the MarketData
    MarketData.objects.create(
        paper_trade=trade,
        timestamp=end_date,
        price=price,
        st=st,
        super_trend_status='long' if st > price else 'short',
        trade_indicator=False  # Set true based on your specific condition
    )
    print("Market data saved.")