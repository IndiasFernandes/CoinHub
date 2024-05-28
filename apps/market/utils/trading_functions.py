from datetime import timedelta, timezone, datetime
import ccxt
from django.shortcuts import get_object_or_404
from apps.exchanges.models import Exchange
from apps.exchanges.utils.hyperliquid.download_data import download_data
from apps.market.backtesting.backtest_utils import run_backtest
from apps.market.models import PaperTrade, MarketData

def paper_trade_execute(trade_id):
    try:
        trade = PaperTrade.objects.get(id=trade_id)
        print(f"Trade: {trade}, Type: {type(trade)}")
    except PaperTrade.DoesNotExist:
        print("Trade not found.")
        return  # Optionally log this error

    if not trade.is_active:
        print("Trade is not active.")
        return  # Trade is not active, do nothing

    # Fetch exchange details from Exchange model using id_char
    exchange = get_object_or_404(Exchange, id_char=trade.exchange)
    print(f"Exchange: {exchange}, Type: {type(exchange)}")
    key = exchange.api_key
    secret = exchange.secret_key

    # Initialize the exchange instance, assuming CCXT usage
    exchange_class = getattr(ccxt, exchange.id_char)  # Ensure the name matches the CCXT identifier
    exchange_instance = exchange_class({
        'apiKey': key,
        'secret': secret,
        'timeout': 30000,
        'enableRateLimit': True,
    })
    print(f"Exchange Instance: {trade.exchange}, Type: {type(trade.exchange)}")

    # Define the timeframe for data to be fetched
    end_date = datetime.now()
    start_date = end_date - timedelta(days=trade.lookback_period)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print(f"Coin: {trade.coin}, Type: {type(trade.coin)}")
    print(f"Timeframe: {trade.timeframe}, Type: {type(trade.timeframe)}")
    print(f"Start Date: {start_date_str}, Type: {type(start_date_str)}")
    print(f"End Date: {end_date_str}, Type: {type(end_date_str)}")
    print(f"Exchange: {exchange_instance}, Type: {type(exchange_instance)}")

    # Download data using the utility function
    df = download_data(trade.coin, trade.timeframe, start_date_str, end_date_str, str(trade.exchange))
    print(f"Downloaded data: {df}, Type: {type(df)}")


    # Run backtest using the utility function
    st, price = run_backtest(trade.coin, df, trade.timeframe, trade.initial_balance, trade.commission, trade.openbrowser)
    print(f"Backtest results: st: {st}, Type: {type(st)}, price: {price}, Type: {type(price)}")

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
