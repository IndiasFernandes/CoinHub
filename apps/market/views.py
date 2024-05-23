import ccxt
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views import View
from .models import Backtest, Optimize, PaperTrade, MarketData
from apps.exchanges.utils.hyperliquid.download_data import initialize_exchange, download_data
from .backtesting.backtest_utils import run_backtest
from .backtesting.optimize_utils import run_optimization
from ..exchanges.models import DownloadDataForm
from ..exchanges.utils.utils import run_exchange

cash = 10000
commission = .008
openbrowser = False
max_tries = 60
atr_timeperiod_range = np.arange(0, 3, 0.2)
atr_multiplier_range = np.arange(0, 3, 0.2)




def run_backtest_view(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange_id']
            key = form.cleaned_data['api_key']
            secret = form.cleaned_data['secret']

            exchange = run_exchange(exchange_id, key, secret)

            symbols = form.cleaned_data['symbol']
            timeperiods = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            results = []

            for symbol in symbols:
                for timeperiod in timeperiods:
                    print(f"Running backtest for {symbol} ({timeperiod})")
                    df = download_data(symbol, timeperiod, start_date, end_date, exchange)
                    st, price = run_backtest(symbol, df, timeperiod)
                    results.append({"symbol": symbol, "timeframe": timeperiod, "st": st, "price": price})

            messages.success(request, "Backtest completed successfully.")
            return JsonResponse({'results': results})
        else:
            messages.error(request, "Form data is invalid.")
    else:
        form = DownloadDataForm()
    return render(request, 'pages/market/backtest_form.html', {
        'form': form,
        'current_section': 'market',
        'section': 'run_backtest',
        'show_sidebar': True
    })

def run_optimization_view(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange_id']
            exchange = initialize_exchange(exchange_id, api_key='your_api_key', secret='your_secret')
            symbols = form.cleaned_data['symbol']
            timeperiods = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            results = []

            for symbol in symbols:
                for timeperiod in timeperiods:
                    df = download_data([symbol], [timeperiod], start_date, end_date, exchange)
                    run_optimization(symbol, timeperiod, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range, atr_multiplier_range)
                    results.append({"symbol": symbol, "timeframe": timeperiod})

            messages.success(request, "Optimization completed successfully.")
            return JsonResponse({'results': results})
        else:
            messages.error(request, "Form data is invalid.")
    else:
        form = DownloadDataForm()
    return render(request, 'pages/market/optimize_form.html', {
        'form': form,
        'current_section': 'market',
        'section': 'run_optimization',
        'show_sidebar': True
    })

def backtests_list_view(request):
    backtests = Backtest.objects.all()
    return render(request, 'pages/market/backtests_list.html', {
        'backtests': backtests,
        'current_section': 'market',
        'section': 'backtests_list',
        'show_sidebar': True
    })

def backtest_detail_view(request, backtest_id):
    backtest = get_object_or_404(Backtest, id=backtest_id)
    return render(request, 'pages/market/backtest_detail.html', {
        'backtest': backtest,
        'current_section': 'market',
        'section': 'backtest_detail',
        'show_sidebar': True
    })

def optimize_list_view(request):
    optimizations = Optimize.objects.all()
    return render(request, 'pages/market/optimize_list.html', {
        'optimizations': optimizations,
        'current_section': 'market',
        'section': 'optimize_list',
        'show_sidebar': True
    })

def optimize_detail_view(request, optimize_id):
    optimization = get_object_or_404(Optimize, id=optimize_id)
    return render(request, 'pages/market/optimize_detail.html', {
        'optimization': optimization,
        'current_section': 'market',
        'section': 'optimize_detail',
        'show_sidebar': True
    })

class PaperTradingDashboardView(View):
    def get(self, request):
        paper_trades = PaperTrade.objects.all()
        market_data = MarketData.objects.all()

        context = {
            'paper_trades': paper_trades,
            'market_data': market_data,
            'current_section': 'market',
            'section': 'paper_trading_dashboard',
            'show_sidebar': True
        }
        return render(request, 'pages/market/paper_trading_dashboard.html', context)

class CreatePaperTradeView(View):
    def post(self, request):
        trade_name = request.POST.get('trade_name')
        initial_balance = request.POST.get('initial_balance')

        if trade_name and initial_balance:
            PaperTrade.objects.create(
                name=trade_name,
                initial_balance=initial_balance,
                created_at=timezone.now()
            )
        return redirect('market:paper_trading_dashboard')
