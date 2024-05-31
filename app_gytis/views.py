import os
import pandas as pd
import ccxt
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import UploadFileForm
from .utils import download_binance_data

def process_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            # Assuming the Excel file has columns: 'coin', 'trade_entry_time'
            df['96_candle_ago_close_price'] = df.apply(
                lambda row: download_binance_data(row['coin'], row['trade_entry_time']), axis=1)

            output_file_path = os.path.join(settings.MEDIA_ROOT, 'output.csv')
            df.to_csv(output_file_path, index=False)

            with open(output_file_path, 'rb') as f:
                response = HttpResponse(f, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=output.csv'
                return response
    else:
        form = UploadFileForm()
    return render(request, 'app_gytis/data_processor.html', {'form': form})

def download_binance_data(coin, trade_entry_time):
    # Initialize the exchange
    exchange = ccxt.binance({
        'rateLimit': 1200,
        'enableRateLimit': True,
    })

    # Calculate the timestamp for 96 candles ago on a 15-minute timeframe
    timeframe = '15m'
    since = exchange.parse8601(trade_entry_time) - 96 * 15 * 60 * 1000  # 96 * 15 minutes in milliseconds

    # Fetch the historical data
    ohlcv = exchange.fetch_ohlcv(coin, timeframe, since, limit=1)

    if ohlcv:
        return ohlcv[0][4]  # Return the closing price
    return None
