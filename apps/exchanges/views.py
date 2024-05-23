from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exchange, Market, Coin, ExchangeInfo, DownloadDataForm
from .forms import ExchangeForm
import requests
from .utils.hyperliquid.bot import BotAccount
from .utils.hyperliquid.download_data import download_data, initialize_exchange

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
    try:
        bot_account = BotAccount()
        coins_prices = bot_account.all_coins()
        for coin_symbol in coins_prices:
            coin, created = Coin.objects.get_or_create(symbol=coin_symbol)
            market.coins.add(coin)
        market.save()
        messages.success(request, "Market coins updated successfully.")
    except requests.RequestException as e:
        messages.error(request, f"Failed to update market coins: {e}")
    return redirect('exchange:exchange_detail', exchange_id=market.exchange.pk)




@login_required
def download_data_view(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            
            api_key = 'your_api_key'
            secret = 'your_secret'
            exchange = initialize_exchange(exchange_id, api_key, secret)
            symbols = form.cleaned_data['symbol']
            timeframes = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            download_data(symbols, timeframes, start_date, end_date, exchange)
            messages.success(request, "Market coins downloaded successfully.")
            return redirect('exchange:download_data')
    else:
        form = DownloadDataForm()
    return render(request, 'pages/exchanges/download_data.html', {
        'form': form,
        'current_section': 'exchanges',
        'section': 'download_data',
        'show_sidebar': True
    })
