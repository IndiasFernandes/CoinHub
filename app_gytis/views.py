import os
import pandas as pd
import ccxt
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta

import time


def process_file_view(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        print(f"File uploaded: {filename}")

        # Read the CSV file
        df = pd.read_csv(file_path)
        print("CSV file read successfully.")

        # Convert 'exit_time' to datetime
        try:
            df['exit_time'] = pd.to_datetime(df['exit_time'], format='%m/%d/%y %H:%M')
            print("Converted 'exit_time' to datetime.")
        except ValueError as e:
            print(f"Error parsing 'exit_time': {e}")
            return HttpResponse(f"Error parsing 'exit_time': {e}", status=400)

        # Check if 'exit_time' is properly parsed
        if df['exit_time'].isnull().any():
            print("Some 'exit_time' values are missing or not properly formatted.")
            return HttpResponse("Some 'exit_time' values are missing or not properly formatted.", status=400)

        # Standardize the coin names
        df['coin'] = df['coin'].apply(standardize_coin_name)
        print("Coin names standardized.")

        # Initialize new columns for entry and exit values
        df['entry_time'] = None
        df['entry_value'] = None
        df['exit_value'] = None

        # Process each unique coin separately
        unique_coins = df['coin'].unique()
        total_coins = len(unique_coins)
        for coin_index, coin in enumerate(unique_coins):
            print(f"Processing coin {coin_index + 1}/{total_coins}: {coin}")
            coin_df = df[df['coin'] == coin].copy()

            for index, row in coin_df.iterrows():
                print(f"Processing {row['coin']} entry {index + 1}/{len(coin_df)}")
                entry_time, entry_value, exit_value = download_binance_data(row['coin'], row['exit_time'])
                coin_df.at[index, 'entry_time'] = entry_time
                coin_df.at[index, 'entry_value'] = entry_value
                coin_df.at[index, 'exit_value'] = exit_value

            # Save the modified DataFrame for each coin to a new CSV file
            output_file_path = os.path.join(settings.BASE_DIR, 'static', 'Gytis', f'{coin.replace("/", "_")}_output.csv')
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            coin_df = coin_df[['coin', 'entry_time', 'entry_value', 'exit_time', 'exit_value']]
            coin_df.to_csv(output_file_path, index=False)
            print(f"Modified DataFrame for {coin} saved to {output_file_path}.")

        # Provide a response indicating the process is complete
        return HttpResponse("Processing complete. Check the static/Gytis folder for output files.")

    return render(request, 'app_gytis/data_processor.html')

def download_binance_data(coin, exit_time, max_retries=5):
    exchange = ccxt.binanceusdm({
        'rateLimit': 1200,
        'enableRateLimit': True,
    })
    print(f"Connecting to Binance perpetuals for coin: {coin}")

    # Convert the exit_time to a timestamp in milliseconds
    try:
        trade_exit_timestamp = int(exit_time.timestamp() * 1000)
        print(f"Converted 'exit_time' to timestamp for coin: {coin}")
    except Exception as e:
        print(f"Error converting 'exit_time' for {coin}: {e}")
        return [None, None, None]  # Handle the error by returning None or some default value

    if trade_exit_timestamp is None:
        print(f"Trade exit time is None for {coin}")
        return [None, None, None]

    since = trade_exit_timestamp - 96 * 15 * 60 * 1000  # 96 * 15 minutes in milliseconds
    print(f"Fetching data for {coin} from {datetime.utcfromtimestamp(since / 1000).strftime('%Y-%m-%d %H:%M:%S')} to {exit_time}")

    retries = 0
    while retries < max_retries:
        try:
            ohlcv = exchange.fetch_ohlcv(coin, '15m', since=since, limit=97)  # Fetch 97 candles to get the 96th candle ago
            print(f"Fetched {len(ohlcv)} candles for {coin}")
            break  # Exit the loop if the fetch is successful
        except Exception as e:
            print(f"Error fetching data for {coin}: {e}")
            retries += 1
            wait_time = 10 * (2 ** (retries - 1))  # Exponential backoff: 10s, 20s, 40s, 80s, ...
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    else:
        print(f"Failed to fetch data for {coin} after {max_retries} retries.")
        return [None, None, None]

    if len(ohlcv) < 97:
        print(f"Not enough data for {coin} at trade_exit_time {exit_time}")
        return [None, None, None]

    entry_time = datetime.utcfromtimestamp(ohlcv[0][0] / 1000)  # Timestamp of the 96th candle ago
    entry_value = ohlcv[0][4]  # Close price of the 96th candle ago
    print(f"96th candle close price for {coin} at {entry_time}: {entry_value}")

    # The latest close price for the exit value
    exit_value = ohlcv[-1][4]  # Close price of the exit time
    print(f"Current close price for {coin}: {exit_value} at {exit_time}")

    return [entry_time, entry_value, exit_value]

def standardize_coin_name(coin):
    mapping = {
        'BTC': 'BTC/USDT',
        'ETH': 'ETH/USDT',
        'AAVE': 'AAVE/USDT',
        'EGLD': 'EGLD/USDT',
        'CFX': 'CFX/USDT',
        # Add more mappings as needed
    }
    standardized_name = mapping.get(coin.upper(), f'{coin}/USDT')
    print(f"Standardized coin name: {coin} to {standardized_name}")
    return standardized_name
