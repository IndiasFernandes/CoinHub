import os, json
from django.views.decorators.csrf import csrf_exempt

import logging
from datetime import datetime

import ccxt
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .exchange_data import EXCHANGES
from .models import Exchange, Market, Coin, ExchangeInfo
from .forms import ExchangeForm, DownloadDataForm  # Ensure both forms are imported correctly
import requests

from .utils.fetch_exchange_data import fetch_all_exchange_data
from .utils.hyperliquid.download_data import download_data, initialize_exchange
from .utils.utils import run_exchange, get_coins, run_update

# Get an instance of a logger
logger = logging.getLogger('django')

from django.urls import reverse
from .forms import MarketForm




def add_market(request, exchange_id):
    exchange = get_object_or_404(Exchange, id=exchange_id)

    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            market = form.save(commit=False)
            market.exchange = exchange
            market.save()
            form.save_m2m()  # To save many-to-many relations
            return redirect(reverse('exchange:exchange_detail', args=[exchange_id]))
    else:
        form = MarketForm()

    return render(request, 'pages/exchanges/add_market.html', {'form': form, 'exchange': exchange, 'current_section': 'exchanges', 'show_sidebar': True})

@login_required
def exchange_list(request):
    exchanges = Exchange.objects.all()
    return render(request, 'pages/exchanges/exchange_list.html', {
        'exchanges': exchanges,
        'current_section': 'exchanges',
        'section': 'exchange_list',
        'show_sidebar': True
    })


@login_required
def exchange_detail(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id)
    return render(request, 'pages/exchanges/exchange_detail.html', {
        'exchange': exchange,
        'current_section': 'exchanges',
        'section': 'exchange_detail',
        'show_sidebar': True
    })


@login_required
def exchange_new(request):
    if request.method == 'POST':
        form = ExchangeForm(request.POST)
        if form.is_valid():
            exchange = form.save()
            return redirect('exchange:exchange_detail', exchange_id=exchange.pk)
    else:
        form = ExchangeForm()
    return render(request, 'pages/exchanges/exchange_new.html', {
        'form': form,
        'current_section': 'exchanges',
        'section': 'exchange_new',
        'show_sidebar': True
    })


@login_required
def chart_view(request):
    exchange_infos = ExchangeInfo.objects.all().order_by('timestamp')
    timestamps = [info.timestamp.strftime("%Y-%m-%d %H:%M:%S") for info in exchange_infos]
    account_values = [float(info.account_value) for info in exchange_infos]
    withdrawable_values = [float(info.withdrawable) for info in exchange_infos]

    context = {
        'timestamps': timestamps,
        'account_values': account_values,
        'withdrawable_values': withdrawable_values,
        'current_section': 'market',
        'section': 'chart_view',
        'show_sidebar': True
    }
    return render(request, 'pages/general/graphs/chart.html', context)



@login_required
def update_market_coins(request, market_id):
    market = get_object_or_404(Market, pk=market_id)
    exchange = market.exchange

    if request.method == 'POST':
        form = MarketForm(request.POST, instance=market)
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange'].id_char
            exchange = get_object_or_404(Exchange, id_char=exchange_id)
            key = exchange.api_key
            secret = exchange.secret_key

            if exchange_id == 'hyperliquid':
                url = 'https://api.hyperliquid.xyz/info'
                headers = {'Content-Type': 'application/json'}
                data = {'type': 'allMids'}
                response = requests.post(url, headers=headers, json=data)
                symbols = response.json().keys()
            elif exchange_id == 'binance':
                url = 'https://api.binance.com/api/v3/exchangeInfo'
                response = requests.get(url)
                data = response.json()
                symbols = [s['symbol'] for s in data['symbols']]
            else:
                exchange_instance = run_exchange(exchange_id, key, secret)
                symbols = get_coins(exchange_instance)

            try:
                market.coins.clear()  # Clear existing coins
                for symbol in symbols:
                    coin, created = Coin.objects.get_or_create(symbol=symbol)
                    market.coins.add(coin)
                market.save()
                messages.success(request, "Market coins updated successfully.")
            except requests.RequestException as e:
                messages.error(request, f"Failed to update market coins: {e}")
            return redirect('exchange:exchange_detail', exchange_id=market.exchange.pk)
    else:
        form = MarketForm(instance=market)

    return render(request, 'pages/exchanges/update_market_coins.html', {'form': form, 'market': market})

@login_required
def download_data_view(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange_id']
            exchange = get_object_or_404(Exchange, id_char=exchange_id)

            key = exchange.api_key
            secret = exchange.secret_key

            exchange_instance = run_exchange(exchange_id, key, secret)

            symbols = form.cleaned_data['symbol']
            timeframes = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')

            downloaded_symbols = []
            start_time = datetime.now()

            for symbol in symbols:
                for timeframe in timeframes:
                    file_path = f"static/data/{exchange_id}/{timeframe}/{symbol.replace('/', '_')}.csv"
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted existing file: {file_path}")

                    print(f"Downloading data for {symbol} ({timeframe})")
                    download_data([symbol], [timeframe], start_date, end_date, exchange_instance)
                    downloaded_symbols.append(f"{symbol} ({timeframe})")

            end_time = datetime.now()
            duration = end_time - start_time

            if downloaded_symbols:
                message = f"Market coins downloaded successfully for the following symbols and timeframes: {', '.join(downloaded_symbols)}"
                logger.info(f"Downloaded symbols and timeframes: {', '.join(downloaded_symbols)}")
                logger.info(f"Download started at: {start_date}, ended at: {end_date}, duration: {duration}")
            else:
                message = "No data was downloaded."
                logger.info("No data was downloaded.")

            messages.success(request, message)
            return redirect('exchange:download_data')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")

    else:
        form = DownloadDataForm()
    return render(request, 'pages/exchanges/download_data.html', {
        'form': form,
        'current_section': 'exchanges',
        'section': 'download_data',
        'show_sidebar': True
    })


def get_exchange_data(request, exchange_id_char):
    try:
        exchange = Exchange.objects.get(id_char=exchange_id_char)
    except Exchange.DoesNotExist:
        return JsonResponse({'error': 'Exchange not found'}, status=404)

    symbols = Coin.objects.filter(markets__exchange=exchange).distinct()
    timeframes = Market.objects.filter(exchange=exchange).values_list('market_type', flat=True).distinct()

    data = {
        'symbols': [symbol.symbol for symbol in symbols],
        'timeframes': list(timeframes)
    }
    return JsonResponse(data)

def list_exchanges():
    return ccxt.exchanges

def fetch_market_types(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)()
    markets = exchange_class.load_markets()
    market_types = set(market.get('type', 'spot') for market in markets.values())
    return market_types

def fetch_markets(exchange_id, market_type):
    exchange_class = getattr(ccxt, exchange_id)()
    markets = exchange_class.load_markets()
    symbols = [symbol for symbol, market in markets.items() if market.get('type', 'spot') == market_type]
    return symbols

@login_required
@csrf_exempt
def update_exchange_markets(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        body = json.loads(request.body)
        if 'exchange_id' in body and 'market_type' not in body:
            exchange_id = body['exchange_id']
            market_types = fetch_market_types(exchange_id)
            return JsonResponse({'market_types': list(market_types)})
        elif 'exchange_id' in body and 'market_type' in body:
            exchange_id = body['exchange_id']
            market_type = body['market_type']
            symbols = fetch_markets(exchange_id, market_type)
            return JsonResponse({'symbols': symbols})
        elif 'update_exchange_id' in body:
            exchange_id = body['update_exchange_id']
            update_exchange_in_db(exchange_id)
            return JsonResponse({'message': f'{exchange_id} updated successfully.'})

    return render(request, 'pages/exchanges/update_exchange_page.html', {
        'exchanges': list_exchanges(),
        'current_section': 'exchanges',
        'section': 'update_exchange_markets',
        'show_sidebar': True
    })

@login_required
def load_markets(request):
    exchange_id = request.GET.get('exchange')
    markets = Market.objects.filter(exchange_id=exchange_id).all()
    return JsonResponse(list(markets.values('id', 'market_type')), safe=False)

@login_required
def load_symbols_and_timeframes(request):
    market_id = request.GET.get('market')
    coins = Coin.objects.filter(markets__id=market_id).distinct().values('symbol')
    # Define a list of timeframes directly or fetch them from a model if they are stored in the database.
    timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M']
    data = {
        'symbols': list(coins),
        'timeframes': timeframes,
    }
    return JsonResponse(data)

def update_exchange_in_db(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)()
    markets = exchange_class.load_markets()

    exchange, created = Exchange.objects.get_or_create(
        id_char=exchange_id,
        defaults={'name': exchange_class.name}
    )

    if not created:
        Market.objects.filter(exchange=exchange).delete()

    for market_id, market_data in markets.items():
        market_type = market_data.get('type', 'spot')
        market, created = Market.objects.get_or_create(
            exchange=exchange,
            market_type=market_type
        )
        symbol = market_data['symbol']
        coin, _ = Coin.objects.get_or_create(symbol=symbol)
        market.coins.add(coin)
    market.save()