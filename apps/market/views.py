
import numpy as np
import warnings
from django.views.decorators.http import require_POST
from django_celery_beat.models import PeriodicTask
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import  redirect
from django.contrib import messages
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import PaperTrade, MarketData, Backtest, Optimize
from .forms import BacktestForm, OptimizeForm, CreatePaperTradeForm
from ..exchanges.utils.utils import run_exchange
from ..exchanges.utils.hyperliquid.download_data import download_data
from .backtesting.backtest_utils import run_backtest
from .backtesting.optimize_utils import run_optimization
from ..exchanges.models import Exchange, Market, Coin

@login_required
def market_dashboard_view(request):
    return render(request, 'pages/market/dashboard.html', {
        'current_section': 'market',
        'section': 'dashboard',
        'show_sidebar': True
    })

@login_required
def load_markets(request):
    exchange_id = request.GET.get('exchange')
    exchange = get_object_or_404(Exchange, id_char=exchange_id)
    markets = Market.objects.filter(exchange=exchange).values('id', 'market_type')
    return JsonResponse(list(markets), safe=False)

@login_required
def load_symbols_and_timeframes(request):
    market_id = request.GET.get('market')
    coins = Coin.objects.filter(markets__id=market_id).distinct()
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    data = {
        'symbols': list(coins.values('id', 'symbol')),
        'timeframes': timeframes
    }
    return JsonResponse(data)

@login_required
def run_backtest_view(request):
    warnings.simplefilter(action='ignore', category=FutureWarning)
    exchanges = Exchange.objects.all()
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            exchange_id = form.cleaned_data['exchange']
            exchange = get_object_or_404(Exchange, id_char=exchange_id)
            key = exchange.api_key
            secret = exchange.secret_key

            exchange_instance = run_exchange(exchange_id, key, secret)
            symbols = form.cleaned_data.get('symbol')
            timeframes = form.cleaned_data.get('timeframe')
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            cash = form.cleaned_data['cash']
            commission = form.cleaned_data['commission']
            openbrowser = form.cleaned_data['openbrowser']
            results = []

            form_data = {
                "exchange": exchange_id,
                "symbols": symbols,
                "timeframes": timeframes,
                "start_date": start_date,
                "end_date": end_date,
                "cash": cash,
                "commission": commission,
                "openbrowser": openbrowser
            }
            print("Backtest Form Data:", form_data)

            if not isinstance(symbols, list):
                symbols = [symbols]
            if not isinstance(timeframes, list):
                timeframes = [timeframes]

            for symbol in symbols:
                for timeframe in timeframes:
                    print(f"Running backtest for {symbol} ({timeframe})")
                    df = download_data(symbol, timeframe, start_date, end_date, exchange_instance)
                    print("Downloaded data.")
                    st, price = run_backtest(symbol, df, timeframe, cash, commission, openbrowser)
                    print("Backtest results: st: ", st, ", price:", price)
                    results.append({"symbol": symbol, "timeframe": timeframe, "st": st, "price": price})

            messages.success(request, "Backtest completed successfully.")
            return redirect('market:run_backtest')
        else:
            print("Form is invalid.")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {form[field].label}: {error}")
                    messages.error(request, f"Error in {form[field].label}: {error}")
    else:
        form = BacktestForm()

    return render(request, 'pages/market/backtest_form.html', {
        'form': form,
        'exchanges': exchanges,
        'current_section': 'market',
        'section': 'run_backtest',
        'show_sidebar': True
    })

@login_required
def run_optimization_view(request):
    warnings.simplefilter(action='ignore', category=FutureWarning)
    exchanges = Exchange.objects.all()
    if request.method == 'POST':
        form = OptimizeForm(request.POST)
        timeframes = list(request.POST.getlist('timeframe'))
        symbols = list(request.POST.getlist('symbol'))
        print("Symbols:", symbols)
        print("Timeframes:", timeframes)
        if form.is_valid():
            exchange_id_char = form.cleaned_data['exchange']
            exchange = get_object_or_404(Exchange, id_char=exchange_id_char)
            key = exchange.api_key
            secret = exchange.secret_key

            exchange_instance = run_exchange(exchange.id_char, key, secret)
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
            atr_timeperiod_range = np.arange(min_timeperiod, max_timeperiod + interval_timeperiod, interval_timeperiod)
            atr_multiplier_range = np.arange(min_multiplier, max_multiplier + interval_multiplier, interval_multiplier)
            timerSymbol = 1
            timerTimeframe = 1

            if not isinstance(symbols, list):
                symbols = [symbols]
            if not isinstance(timeframes, list):
                timeframes = [timeframes]

            for symbol in symbols:
                print(f"{timerSymbol}/{len(symbols)}: Symbol {symbol}")
                timerSymbol += 1
                for timeframe in timeframes:
                    print(f"{timerTimeframe}/{len(timeframes)}: Timeframe {timeframe}")
                    timerTimeframe += 1
                    df = download_data(symbol, timeframe, start_date, end_date, exchange_instance)
                    stats, heatmap = run_optimization(symbol, timeframe, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range, atr_multiplier_range, exchange_instance)

            messages.success(request, "Optimization completed successfully.")
            return redirect('market:run_optimization')
        else:
            print("Form is invalid.")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {form[field].label}: {error}")
                    messages.error(request, f"Error in {form[field].label}: {error}")
    else:
        form = OptimizeForm()

    return render(request, 'pages/market/optimize_form.html', {
        'form': form,
        'exchanges': exchanges,
        'current_section': 'market',
        'section': 'run_optimization',
        'show_sidebar': True
    })

@login_required
def backtests_list_view(request):
    backtests = Backtest.objects.all()
    return render(request, 'pages/market/backtests_list.html', {
        'backtests': backtests,
        'current_section': 'market',
        'section': 'backtests_list',
        'show_sidebar': True
    })

@login_required
def backtest_detail_view(request, backtest_id):
    backtest = get_object_or_404(Backtest, id=backtest_id)
    return render(request, 'pages/market/backtest_detail.html', {
        'backtest': backtest,
        'current_section': 'market',
        'section': 'backtest_detail',
        'show_sidebar': True
    })

@login_required
def optimize_list_view(request):
    optimizations = Optimize.objects.all()
    return render(request, 'pages/market/optimize_list.html', {
        'optimizations': optimizations,
        'current_section': 'market',
        'section': 'optimize_list',
        'show_sidebar': True
    })

@login_required
def optimize_detail_view(request, optimize_id):
    optimization = get_object_or_404(Optimize, id=optimize_id)

    return render(request, 'pages/market/optimize_detail.html', {
        'optimization': optimization,
        'current_section': 'market',
        'section': 'optimize_detail',
        'show_sidebar': True
    })

@login_required
def paper_trading_dashboard_view(request):
    paper_trades = PaperTrade.objects.all()
    market_data = MarketData.objects.all()

    context = {
        'paper_trades': paper_trades,
        'market_data': market_data,
        'current_section': 'market',
        'section': 'paper_trading_dashboard',
        'show_sidebar': True
    }
    return render(request, 'pages/market/paper_trade_dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class CreatePaperTradeView(View):
    def get(self, request):
        form = CreatePaperTradeForm()
        context = {
            'form': form,
            'exchanges': Exchange.objects.all(),
            'markets': Market.objects.all(),
            'symbols': Coin.objects.all()
        }
        return render(request, 'pages/market/paper_trade_create.html', context)

    def post(self, request):
        form = CreatePaperTradeForm(request.POST)
        print(f"POST data: {request.POST}")
        print(f"Form valid: {form.is_valid()}")

        if form.is_valid():
            paper_trade = form.save(commit=False)
            coin_id = request.POST.get('coin')
            market_id = request.POST.get('type')

            try:
                coin = Coin.objects.get(id=coin_id)
                market = Market.objects.get(id=market_id)

                paper_trade.coin = coin.symbol
                paper_trade.type = market.market_type
            except (Coin.DoesNotExist, Market.DoesNotExist):
                messages.error(request, "Selected coin or market does not exist.")
                context = {
                    'form': form,
                    'exchanges': Exchange.objects.all(),
                    'markets': Market.objects.all(),
                    'symbols': Coin.objects.all()
                }
                return render(request, 'pages/market/paper_trade_create.html', context)

            paper_trade.save()
            messages.success(request, "Paper trade created successfully!")
            return redirect('market:paper_trading_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {form[field].label}: {error}")
            messages.error(request, "Error creating paper trade. Please check the form for errors.")
            print(f"Form errors: {form.errors}")
            return render(request, 'pages/market/paper_trade_create.html',
                          {'form': form, 'exchanges': Exchange.objects.all(), 'markets': Market.objects.all(),
                           'symbols': Coin.objects.all()})



@login_required
def paper_trade_detail_view(request, trade_id):
    paper_trade = get_object_or_404(PaperTrade, pk=trade_id)
    market_data = MarketData.objects.filter(paper_trade_id=trade_id).order_by('timestamp')

    timestamps = [md.timestamp.isoformat() for md in market_data]
    prices = [float(md.price) for md in market_data]
    st_values = [float(md.st) for md in market_data]

    context = {
        'paper_trade': paper_trade,
        'timestamps': json.dumps(timestamps, cls=DjangoJSONEncoder),
        'prices': json.dumps(prices),
        'st_values': json.dumps(st_values),
    }
    return render(request, 'pages/market/paper_trade_detail.html', context)

def fetch_market_data(request, trade_id):
    try:
        market_data = MarketData.objects.filter(paper_trade_id=trade_id).order_by('timestamp')
        timestamps = [md.timestamp.isoformat() for md in market_data]
        prices = [float(md.price) for md in market_data]
        st_values = [float(md.st) for md in market_data]

        data = {
            'timestamps': timestamps,
            'prices': prices,
            'st_values': st_values,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
class TogglePaperTradingView(View):
    def post(self, request, trade_id):
        paper_trade = get_object_or_404(PaperTrade, pk=trade_id)
        paper_trade.is_active = not paper_trade.is_active
        paper_trade.save()

        task_name = f'PaperTrade_{paper_trade.id}_task'
        try:
            task = PeriodicTask.objects.get(name=task_name)
            task.enabled = paper_trade.is_active
            task.save()
            message = f"{'Activated' if paper_trade.is_active else 'Deactivated'} task {task_name}."
            print(message)
        except PeriodicTask.DoesNotExist:
            message = f"No periodic task found for {task_name}."
            print(message)

        return JsonResponse({"status": "success", "is_active": paper_trade.is_active, "message": message})

@require_POST
@login_required
def delete_paper_trade(request, trade_id):
    trade = get_object_or_404(PaperTrade, pk=trade_id)
    trade.delete()
    return JsonResponse({'status': 'success', 'message': 'Trade deleted successfully'})
