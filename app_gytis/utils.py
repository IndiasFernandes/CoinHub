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

import os
import pandas as pd

def join_csv_files(input_folder, output_file):
    combined_data = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            print(f"Processing file: {file_path}")

            # Read each CSV file
            df = pd.read_csv(file_path)

            # Ensure the required columns are present
            if {'coin', 'entry_time', 'entry_value', 'exit_time', 'exit_value'}.issubset(df.columns):
                # Rename columns to match the required output
                df = df.rename(columns={'entry_time': 'trade_entry_time', 'entry_value': 'price_24h_before'})
                df = df[['coin', 'trade_entry_time', 'price_24h_before']]

                combined_data.append(df)
            else:
                print(f"Skipping file {file_path}: Required columns are missing.")

    # Combine all data into a single DataFrame
    combined_df = pd.concat(combined_data, ignore_index=True)

    # Save the combined DataFrame to the output file
    combined_df.to_csv(output_file, index=False)
    print(f"Combined data saved to {output_file}")

if __name__ == "__main__":
    input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'Gytis')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'Gytis', 'combined_output.csv')

    join_csv_files(input_folder, output_file)
