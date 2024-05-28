from datetime import timezone, timedelta

import ccxt
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.exchanges.models import Exchange
from apps.exchanges.utils.hyperliquid.download_data import download_data
from apps.market.backtesting.backtest_utils import run_backtest
from apps.market.models import PaperTrade, MarketData


def paper_trade_execute(trade_id):
    print(f"Starting paper trade execution for trade ID: {trade_id}")
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        print(f"Trade found: {trade}")
    except PaperTrade.DoesNotExist:
        print(f"Trade with ID {trade_id} not found.")
        return  # Optionally log this error

    if not trade.is_active:
        print(f"Trade with ID {trade_id} is not active.")
        return  # Trade is not active, do nothing

    # Fetch exchange details from Exchange model using id_char
    try:
        exchange = get_object_or_404(Exchange, id_char=trade.exchange)
        print(f"Exchange found: {exchange}")
        # e
    except Exchange.DoesNotExist:
        print(f"Exchange with name {trade.exchange} not found.")
        return  # Optionally log this error

    key = exchange.api_key
    secret = exchange.api_secret

    # Initialize the exchange instance, assuming CCXT usage
    try:
        exchange_class = getattr(ccxt, exchange.name.lower())  # Ensure the name matches the CCXT identifier
        exchange_instance = exchange_class({
            'apiKey': key,
            'secret': secret,
            'timeout': 30000,
            'enableRateLimit': True,
        })
        print(f"Initialized exchange instance for {exchange.name}")
    except AttributeError:
        print(f"Error initializing exchange instance for {exchange.name}")
        return  # Optionally log this error

    # Define the timeframe for data to be fetched
    end_date = timezone.now()
    start_date = end_date - timedelta(days=trade.lookback_period)
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()
    print(f"Fetching data from {start_date_str} to {end_date_str}")

    # Download data using the utility function
    try:
        df = download_data([trade.coin], [trade.timeframe], start_date_str, end_date_str, exchange_instance)
        print("Downloaded data successfully.")
    except Exception as e:
        print(f"Error downloading data: {e}")
        return  # Optionally log this error

    # Run backtest using the utility function
    try:
        st, price = run_backtest(trade.coin, df, trade.timeframe, trade.initial_balance, trade.commission, trade.openbrowser)
        print(f"Backtest results: st={st}, price={price}")
    except Exception as e:
        print(f"Error running backtest: {e}")
        return  # Optionally log this error

    # Create or update the MarketData
    try:
        MarketData.objects.create(
            paper_trade=trade,
            timestamp=end_date,
            price=price,
            st=st,
            super_trend_status='long' if st > price else 'short',
            trade_indicator=False  # Set true based on your specific condition
        )
        print("Market data saved successfully.")
    except Exception as e:
        print(f"Error saving market data: {e}")
