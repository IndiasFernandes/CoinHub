from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import format_html
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import numpy as np
from .models import PaperTrade, MarketData, Backtest, Optimize
from .forms import BacktestForm, OptimizeForm
from ..exchanges.utils.utils import run_exchange
from ..exchanges.utils.hyperliquid.download_data import download_data
from .backtesting.backtest_utils import run_backtest
from .backtesting.optimize_utils import run_optimization
from ..exchanges.models import Exchange, Market, Coin


def market_dashboard_view(request):
    return render(request, 'pages/market/dashboard.html', {
        'current_section': 'market',
        'section': 'dashboard',
        'show_sidebar': True
    })


def run_backtest_view(request):
    exchanges = Exchange.objects.all()
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        form_data = {
            "exchange": request.POST.get('exchange'),
            "symbols": request.POST.getlist('symbol'),
            "timeframes": request.POST.getlist('timeframe'),
            "start_date": request.POST.get('start_date'),
            "end_date": request.POST.get('end_date'),
            "cash": request.POST.get('cash'),
            "commission": request.POST.get('commission'),
            "openbrowser": request.POST.get('openbrowser')
        }
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange']
            exchange = get_object_or_404(Exchange, id_char=exchange_id)
            key = exchange.api_key
            secret = exchange.secret_key

            exchange_instance = run_exchange(exchange_id, key, secret)
            symbols = form.cleaned_data['symbol']
            timeframes = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            cash = form.cleaned_data['cash']
            commission = form.cleaned_data['commission']
            openbrowser = form.cleaned_data['openbrowser']
            results = []

            # Log or display form data
            form_data.update({
                "exchange": exchange_id,
                "symbols": symbols,
                "timeframes": timeframes,
                "start_date": start_date,
                "end_date": end_date,
                "cash": cash,
                "commission": commission,
                "openbrowser": openbrowser
            })
            print("Backtest Form Data:", form_data)  # This will log data to the console

            for symbol in symbols:
                for timeframe in timeframes:
                    df = download_data([symbol], [timeframe], start_date, end_date, exchange_instance)
                    st, price = run_backtest(symbol, df, timeframe, cash, commission, openbrowser)
                    results.append({"symbol": symbol, "timeframe": timeframe, "st": st, "price": price})

            messages.success(request, "Backtest completed successfully.")
            return redirect('market:run_backtest')
        else:
            error_messages = format_html('<ul>{}</ul>', ''.join([format_html('<li>{}: {}</li>', field.label, error) for field in form for error in field.errors]))
            messages.error(request, format_html("Form data is invalid: {}<br>Form Data: {}", error_messages, form_data))
    else:
        form = BacktestForm()

    return render(request, 'pages/market/backtest_form.html', {
        'form': form,
        'exchanges': exchanges,
        'current_section': 'market',
        'section': 'run_backtest',
        'show_sidebar': True
    })


def run_optimization_view(request):
    exchanges = Exchange.objects.all()
    if request.method == 'POST':
        form = OptimizeForm(request.POST)
        if form.is_valid():
            exchange_id_char = form.cleaned_data['exchange']
            exchange = get_object_or_404(Exchange, id_char=exchange_id_char)
            key = exchange.api_key
            secret = exchange.secret_key

            exchange_instance = run_exchange(exchange.id_char, key, secret)
            symbols = form.cleaned_data['symbol']
            timeframes = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            cash = form.cleaned_data['cash']
            commission = form.cleaned_data['commission']
            openbrowser = form.cleaned_data['openbrowser']
            max_tries = form.cleaned_data['max_tries']
            min_timeperiod = form.cleaned_data['min_timeperiod']
            max_timeperiod = form.cleaned_data['max_timeperiod']
            interval_timeperiod = form.cleaned_data['interval_timeperiod']
            min_multiplier = form.cleaned_data['min_multiplier']
            max_multiplier = form.cleaned_data['max_multiplier']
            interval_multiplier = form.cleaned_data['interval_multiplier']
            atr_timeperiod_range = np.arange(min_timeperiod, max_timeperiod, interval_timeperiod)
            atr_multiplier_range = np.arange(min_multiplier, max_multiplier, interval_multiplier)
            results = []

            # Log or display form data
            form_data = {
                "exchange": exchange_id_char,
                "symbols": symbols,
                "timeframes": timeframes,
                "start_date": start_date,
                "end_date": end_date,
                "cash": cash,
                "commission": commission,
                "openbrowser": openbrowser,
                "max_tries": max_tries,
                "min_timeperiod": min_timeperiod,
                "max_timeperiod": max_timeperiod,
                "interval_timeperiod": interval_timeperiod,
                "min_multiplier": min_multiplier,
                "max_multiplier": max_multiplier,
                "interval_multiplier": interval_multiplier
            }
            print("Optimization Form Data:", form_data)  # This will log data to the console

            for symbol in symbols:
                for timeframe in timeframes:
                    df = download_data([symbol], [timeframe], start_date, end_date, exchange_instance)
                    run_optimization(symbol, timeframe, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range, atr_multiplier_range)
                    results.append({"symbol": symbol, "timeframe": timeframe})

            messages.success(request, "Optimization completed successfully.")
            return redirect('market:run_optimization')
        else:
            error_messages = format_html('<ul>{}</ul>', ''.join([format_html('<li>{}: {}</li>', field.label, error) for field in form for error in field.errors]))
            messages.error(request, format_html("Form data is invalid: {}", error_messages))
    else:
        form = OptimizeForm()

    return render(request, 'pages/market/optimize_form.html', {
        'form': form,
        'exchanges': exchanges,
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

from django.http import JsonResponse

@login_required
def load_markets(request):
    exchange_id = request.GET.get('exchange')
    markets = Market.objects.filter(exchange_id=exchange_id).all()
    return JsonResponse(list(markets.values('id', 'market_type')), safe=False)

@login_required
def load_symbols_and_timeframes(request):
    market_id = request.GET.get('market')
    coins = Coin.objects.filter(markets__id=market_id).distinct()
    market = Market.objects.get(id=market_id)
    data = {
        'symbols': list(coins.values('id', 'symbol')),
        'timeframes': [(market.market_type, market.market_type)],
    }
    return JsonResponse(data)