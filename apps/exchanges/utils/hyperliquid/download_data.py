import ccxt
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from django.conf import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')

from apps.exchanges.utils.utils import ensure_dir, merge_and_save_data

def initialize_exchange(exchange_id, api_key, secret):
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True  # Enabling rate limit is important to avoid being banned by the exchange
    })

def heikin_ashi(df):
    df_ha = df.copy()

    df_ha['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    for i in range(len(df)):
        df_ha.at[i, 'Open'] = (df.at[i - 1, 'Open'] + df.at[i - 1, 'Close']) / 2 if i > 0 else df.at[i, 'Open']
        df_ha.at[i, 'High'] = max(df.at[i, 'High'], df.at[i, 'Open'], df.at[i, 'Close'])
        df_ha.at[i, 'Low'] = min(df.at[i, 'Low'], df.at[i, 'Open'], df.at[i, 'Close'])

    return df_ha

def download_data(symbols, timeframes, start_date, end_date, exchange):
    for symbol in symbols:
        for timeframe in timeframes:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

            data_dir = os.path.join(settings.BASE_DIR, 'static', 'data', exchange.id, timeframe)
            ensure_dir(data_dir)
            file_path = os.path.join(data_dir, f'{symbol.replace("/", "_")}.csv')
            #fetch_ohlcv = exchange.fetch_ohlcv(symbol="AAVE/USDC:USDC", timeframe='5m',
            #                                   since=int(datetime(2024, 4, 11).timestamp() * 1000), limit=1000,
            #                                   params={})

            logging.info(f"Downloading data for {symbol} ({timeframe}) to {file_path}")
            all_data = []
            while start_timestamp < end_timestamp:
                try:
                    data = exchange.fetch_ohlcv(symbol, timeframe, since=start_timestamp, limit=1000)
                    if data:
                        start_timestamp = data[-1][0] + 1
                        all_data.extend(data)
                    else:
                        a = 1
                except ccxt.NetworkError as e:
                    logging.error(f"Network error occurred: {e}")
                    break
                except ccxt.ExchangeError as e:
                    logging.error(f"Exchange error occurred: {e}")
                    break

            if all_data:
                df = pd.DataFrame(all_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
                df.set_index('Timestamp', inplace=True)
                merge_and_save_data(df, file_path)

                # Heikin Ashi Conversion
                df_ha = heikin_ashi(df.reset_index())
                df_ha.set_index('Timestamp', inplace=True)
                ha_file_path = os.path.join(data_dir, f'{symbol.replace("/", "_")}_HA.csv')
                merge_and_save_data(df_ha, ha_file_path)
                return df
            else:
                logging.info("No data fetched.")
