import pandas as pd
from datetime import datetime, timedelta
import os
from CoinHub import settings
from apps.exchanges.utils.utils import ensure_dir, merge_and_save_data

import ccxt
from datetime import datetime

exchange_id = 'hyperliquid'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': '0xa9dA24397F0B02eaa39cDBCae312559CaEe17985',
    'secret': '0x00ddedb69741e811a8265d90e94f74e55f34f07f7f810f603b02508e778b91b4',
})

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')
django.setup()

def download_data(symbols, timeframes, start_date, end_date, exchange_id):
    exchange = getattr(ccxt, exchange_id)()

    for symbol in symbols:
        for timeframe in timeframes:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

            # Generate file path
            data_dir = os.path.join(settings.BASE_DIR, 'static','data', exchange_id, timeframe, symbol.replace("/", "_"))
            ensure_dir(data_dir)
            print(data_dir)
            file_path = f'{data_dir}/{start_date}_to_{end_date}.csv'

            # Fetch and save data
            print(f"Downloading data for {symbol} ({timeframe})")
            all_data = []
            while start_timestamp < end_timestamp:
                data = exchange.fetch_ohlcv(symbol, timeframe, since=start_timestamp, limit=1000)
                if data:
                    start_timestamp = data[-1][0] + 1  # prepare the next call to start right after the last data
                    all_data.extend(data)
                else:
                    break  # no more data available
            df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            merge_and_save_data(df, file_path)

symbols = ['AAVE/USDC:USDC', 'ACE/USDC:USDC', 'ADA/USDC:USDC', 'AI/USDC:USDC']
timeframes = ['1h']
start_date = '2000-10-01'
end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday

download_data(symbols, timeframes, start_date, end_date, exchange_id)

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from django.conf import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Utility functions
from apps.exchanges.utils.utils import ensure_dir, merge_and_save_data


def initialize_exchange(exchange_id, api_key, secret):
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True  # Enabling rate limit is important to avoid being banned by the exchange
    })


def download_data(symbols, timeframes, start_date, end_date, exchange):
    for symbol in symbols:
        for timeframe in timeframes:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

            # Prepare the directory path and file
            data_dir = os.path.join(settings.BASE_DIR, 'static', 'data', exchange.id, symbol.replace("/", "_"),
                                    timeframe)
            ensure_dir(data_dir)
            file_path = os.path.join(data_dir, f'{start_date}_to_{end_date}.csv')

            logging.info(f"Downloading data for {symbol} ({timeframe}) to {file_path}")
            all_data = []
            while start_timestamp < end_timestamp:
                try:
                    data = exchange.fetch_ohlcv(symbol, timeframe, since=start_timestamp, limit=1000)
                    if data:
                        start_timestamp = data[-1][0] + 1
                        all_data.extend(data)
                    else:
                        break
                except ccxt.NetworkError as e:
                    logging.error(f"Network error occurred: {e}")
                    break
                except ccxt.ExchangeError as e:
                    logging.error(f"Exchange error occurred: {e}")
                    break

            if all_data:
                df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                merge_and_save_data(df, file_path)
            else:
                logging.info("No data fetched.")


if __name__ == "__main__":
    exchange_id = 'hyperliquid'
    api_key = '0xa9dA24397F0B02eaa39cDBCae312559CaEe17985'
    secret = '0x00ddedb69741e811a8265d90e94f74e55f34f07f7f810f603b02508e778b91b4'
    exchange = initialize_exchange(exchange_id, api_key, secret)

    symbols = ['AAVE/USDC:USDC', 'ACE/USDC:USDC', 'ADA/USDC:USDC', 'AI/USDC:USDC']  # Example symbols
    timeframes = ['1h']  # Example timeframe
    start_date = '2023-01-01'
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    download_data(symbols, timeframes, start_date, end_date, exchange)
