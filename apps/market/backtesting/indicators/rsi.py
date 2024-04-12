import pandas as pd
# import talib
from binance.enums import *


# def get_rsi(client):
#     # Retrieve historical data for BTCUSDT 1-minute candles
#     klines = client.get_historical_klines('BTCUSDT', KLINE_INTERVAL_1MINUTE, '30 minutes ago UTC')
#
#     # Convert data to a Pandas DataFrame
#     df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
#                                        'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
#                                        'taker_buy_quote_asset_volume', 'ignore'])
#
#     # Clean up the DataFrame
#     df = df.drop(['timestamp', 'open', 'high', 'low', 'volume', 'quote_asset_volume', 'num_trades',
#                   'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1)
#     df['close'] = pd.to_numeric(df['close'])
#     df.set_index(pd.to_datetime(df['close_time'], unit='ms'), inplace=True)
#     df.drop('close_time', axis=1, inplace=True)
#
#     # Calculate RSI indicator with a period of 14
#     rsi = talib.RSI(df['close'], timeperiod=14)
#
#     return float(rsi.iloc[-1])


import requests
import pandas as pd

def calculate_rsi(symbol, interval, period):
    """
    Calculate the current RSI for a given symbol on Binance exchange
    based on a specified interval and period.

    Args:
    - symbol: str, the symbol to calculate RSI for (e.g. 'BTCUSDT')
    - interval: str, the interval of the data (default: '1m')
    - period: int, the number of periods to use in the RSI calculation (default: 14)

    Returns:
    - rsi: float, the current RSI value for the given symbol and interval
    """

    # Define the API endpoint and parameters
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': period + 1}

    # Get the data from Binance API
    response = requests.get(url, params=params)
    data = response.json()

    # Convert data to pandas dataframe and clean up
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
                                     'taker_buy_quote_asset_volume', 'ignore'])
    df.drop(['timestamp', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
             'taker_buy_quote_asset_volume', 'ignore'], axis=1, inplace=True)
    df = df.astype(float)

    # Calculate the RSI using the pandas_ta library
    import pandas_ta as ta
    df['rsi'] = ta.rsi(df['close'], length=period)

    # Return the current RSI value
    return df['rsi'].iloc[-1]