import ccxt

def download_binance_data(coin, trade_entry_time, lookback_candles = 96, timeframe_minutes = 15):
    # Initialize the exchange
    exchange = ccxt.binance({
        'rateLimit': 1200,
        'enableRateLimit': True,
    })

    # Calculate the timestamp for 96 candles ago on a 15-minute timeframe
    timeframe = '15m'
    since = exchange.parse8601(trade_entry_time) - lookback_candles * timeframe_minutes * 60 * 1000  # 96 * 15 minutes in milliseconds

    # Fetch the historical data
    ohlcv = exchange.fetch_ohlcv(coin, timeframe, since, limit=1)

    if ohlcv:
        return ohlcv[0][4]  # Return the closing price
    return None

