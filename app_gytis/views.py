import os
import pandas as pd
import ccxt
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from datetime import datetime

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

        # Convert 'entry_time' to datetime
        try:
            df['entry_time'] = pd.to_datetime(df['entry_time'], format='%m/%d/%y %H:%M')
            print("Converted 'entry_time' to datetime.")
        except ValueError as e:
            print(f"Error parsing 'entry_time': {e}")
            return HttpResponse(f"Error parsing 'entry_time': {e}", status=400)

        # Check if 'entry_time' is properly parsed
        if df['entry_time'].isnull().any():
            print("Some 'entry_time' values are missing or not properly formatted.")
            return HttpResponse("Some 'entry_time' values are missing or not properly formatted.", status=400)

        # Standardize the coin names
        df['coin'] = df['coin'].apply(standardize_coin_name)
        print("Coin names standardized.")

        # Process the DataFrame to fill in the 'exit_time' column
        df['exit_time'] = df.apply(
            lambda row: download_binance_data(row['coin'], row['entry_time']), axis=1)
        print("Processed the DataFrame to fill in the 'exit_time' column.")

        # Save the modified DataFrame to a new CSV file
        output_file_path = os.path.join(settings.MEDIA_ROOT, 'output.csv')
        df.to_csv(output_file_path, index=False)
        print(f"Modified DataFrame saved to {output_file_path}.")

        # Provide the modified file as a download response
        with open(output_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=output.csv'
            print("Modified file provided as a download response.")
            return response

    return render(request, 'app_gytis/data_processor.html')

def download_binance_data(coin, entry_time):
    exchange = ccxt.binanceusdm({
        'rateLimit': 1200,
        'enableRateLimit': True,
    })
    print(f"Connecting to Binance perpetuals for coin: {coin}")

    # Convert the entry_time to a timestamp in milliseconds
    try:
        trade_entry_timestamp = int(entry_time.timestamp() * 1000)
        print(f"Converted 'entry_time' to timestamp for coin: {coin}")
    except Exception as e:
        print(f"Error converting 'entry_time' for {coin}: {e}")
        return None  # Handle the error by returning None or some default value

    if trade_entry_timestamp is None:
        print(f"Trade entry time is None for {coin}")
        return None

    since = trade_entry_timestamp - 96 * 15 * 60 * 1000  # 96 * 15 minutes in milliseconds
    print(f"Fetching data for {coin} from {datetime.utcfromtimestamp(since / 1000).strftime('%Y-%m-%d %H:%M:%S')} to {entry_time}")

    ohlcv = exchange.fetch_ohlcv(coin, '15m', since=since, limit=97)  # Fetch 97 candles to get the 96th candle ago
    print(f"Fetched {len(ohlcv)} candles for {coin}")

    if len(ohlcv) < 97:
        print(f"Not enough data for {coin} at trade_entry_time {entry_time}")
        return None

    # The 96th candle ago will be at index 0
    close_price = ohlcv[0][4]  # 4 is the close price in the ohlcv structure
    print(f"96th candle close price for {coin} at {entry_time}: {close_price}")

    return close_price

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
