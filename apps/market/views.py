from _decimal import Decimal

import numpy as np
import warnings
from django.views.decorators.http import require_POST
from django_celery_beat.models import PeriodicTask
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from .models import Backtest, Optimize
from .forms import BacktestForm, OptimizeForm, CreatePaperTradeForm, OptimizationForm
from ..exchanges.utils.utils import run_exchange
from ..exchanges.utils.hyperliquid.download_data import download_data
from .backtesting.backtest_utils import run_backtest
from .backtesting.optimize_utils import run_optimization
from ..exchanges.models import Exchange, Market, Coin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TradeParametersForm  # Ensure this line is present
from .models import PaperTrade, MarketData
import json
from decimal import Decimal
from .models import OptimizationResult

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
                    run_backtest(symbol, df, timeframe, exchange_id, cash, commission, openbrowser)
                    print("Backtest completed successfully.")

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
            'symbols': Coin.objects.all(),
            'optimizations': Optimize.objects.all()  # Fetch all optimizations to display in the table
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
                    'symbols': Coin.objects.all(),
                    'optimizations': Optimize.objects.all()  # Fetch all optimizations to display in the table
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
            context = {
                'form': form,
                'exchanges': Exchange.objects.all(),
                'markets': Market.objects.all(),
                'symbols': Coin.objects.all(),
                'optimizations': Optimize.objects.all()  # Fetch all optimizations to display in the table
            }
            return render(request, 'pages/market/paper_trade_create.html', context)


@login_required
def paper_trade_detail_view(request, trade_id):
    paper_trade = get_object_or_404(PaperTrade, pk=trade_id)
    market_data = MarketData.objects.filter(paper_trade_id=trade_id).order_by('timestamp')

    if request.method == 'POST':
        form = TradeParametersForm(request.POST, instance=paper_trade)
        if form.is_valid():
            form.save()
            calculate_profit(paper_trade, market_data)  # Recalculate profit on parameter change
            messages.success(request, "Parameters updated successfully!")
            return redirect('market:paper_trade_detail', trade_id=trade_id)  # Refresh the page
        else:
            messages.error(request, "Error updating parameters.")
    else:
        form = TradeParametersForm(instance=paper_trade)

    timestamps = [md.timestamp.isoformat() for md in market_data]
    prices = [float(md.price) for md in market_data]
    st_values = [float(md.st) for md in market_data]
    profits = [float(md.profit) for md in market_data]

    total_profit = sum(profits)

    context = {
        'paper_trade': paper_trade,
        'timestamps': json.dumps(timestamps),
        'prices': json.dumps(prices),
        'st_values': json.dumps(st_values),
        'profits': json.dumps(profits),
        'total_profit': total_profit,
        'form': form
    }
    return render(request, 'pages/market/paper_trade_detail.html', context)

from decimal import Decimal

def calculate_profit(paper_trade, market_data):
    initial_account = Decimal(paper_trade.initial_account)
    x_prices = int(paper_trade.x_prices)
    take_profit = Decimal(paper_trade.take_profit) / 100  # Converting to a fraction
    stop_loss = Decimal(paper_trade.stop_loss) / 100  # Converting to a fraction
    fee = Decimal(paper_trade.trading_fee) / 100

    current_balance = initial_account
    open_trade = None  # None, 'buy', or 'short'
    open_trade_price = Decimal('0.0')
    consecutive_above = 0
    consecutive_below = 0

    for data in market_data:
        if open_trade == 'buy':
            if data.price < data.st:
                # Close buy trade when price drops below supertrend
                profit = (data.price - open_trade_price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0
            elif (data.price - open_trade_price) / open_trade_price >= take_profit:
                # Close buy trade when take profit is reached
                profit = (data.price - open_trade_price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0
            elif (open_trade_price - data.price) / open_trade_price >= stop_loss:
                # Close buy trade when stop loss is reached
                profit = (data.price - open_trade_price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0

        elif open_trade == 'short':
            if data.price > data.st:
                # Close short trade when price rises above supertrend
                profit = (open_trade_price - data.price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0
            elif (open_trade_price - data.price) / open_trade_price >= take_profit:
                # Close short trade when take profit is reached
                profit = (open_trade_price - data.price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0
            elif (data.price - open_trade_price) / open_trade_price >= stop_loss:
                # Close short trade when stop loss is reached
                profit = (open_trade_price - data.price) * (1 - fee)
                current_balance += profit
                open_trade = None
                consecutive_above = 0
                consecutive_below = 0

        elif not open_trade:
            if data.price > data.st:
                consecutive_above += 1
                consecutive_below = 0
            elif data.price < data.st:
                consecutive_below += 1
                consecutive_above = 0

            if consecutive_above >= x_prices:
                # Open buy trade
                open_trade = 'buy'
                open_trade_price = data.price
                consecutive_above = 0
            elif consecutive_below >= x_prices:
                # Open short trade
                open_trade = 'short'
                open_trade_price = data.price
                consecutive_below = 0

        data.profit = current_balance - initial_account
        data.save()



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


from django.db import models



@login_required
def optimize_view(request, trade_id):
    paper_trade = get_object_or_404(PaperTrade, pk=trade_id)
    market_data = MarketData.objects.filter(paper_trade_id=trade_id).order_by('timestamp')

    if request.method == 'POST':
        form = OptimizationForm(request.POST)
        if form.is_valid():
            tp_min = form.cleaned_data['take_profit_min']
            tp_max = form.cleaned_data['take_profit_max']
            tp_step = form.cleaned_data['take_profit_step']
            sl_min = form.cleaned_data['stop_loss_min']
            sl_max = form.cleaned_data['stop_loss_max']
            sl_step = form.cleaned_data['stop_loss_step']
            x_min = form.cleaned_data['x_prices_min']
            x_max = form.cleaned_data['x_prices_max']
            x_step = form.cleaned_data['x_prices_step']

            tp_range = [Decimal(tp_min) + i * Decimal(tp_step) for i in range(int((tp_max - tp_min) / tp_step) + 1)]
            sl_range = [Decimal(sl_min) + i * Decimal(sl_step) for i in range(int((sl_max - sl_min) / sl_step) + 1)]
            x_range = [x_min + i * x_step for i in range((x_max - x_min) // x_step + 1)]

            best_tp, best_sl, best_x, best_profit = optimize_parameters(paper_trade, market_data, tp_range, sl_range, x_range)

            messages.success(request, f"Optimization completed! Best TP: {best_tp}, Best SL: {best_sl}, Best X: {best_x}, Profit: ${best_profit}")
            return redirect('market:paper_trade_detail', trade_id=trade_id)
        else:
            messages.error(request, "Error in optimization parameters.")
    else:
        form = OptimizationForm()

    return render(request, 'pages/market/optimize_form.html', {'form': form})

def run_backtest_pt(paper_trade, market_data):
    calculate_profit(paper_trade, market_data)
    total_profit = sum([md.profit for md in market_data])
    return total_profit

def optimize_parameters(paper_trade, market_data, tp_range, sl_range, x_range):
    best_profit = Decimal('-Infinity')
    best_tp = None
    best_sl = None
    best_x = None
    total_iterations = len(tp_range) * len(sl_range) * len(x_range)
    iteration = 0

    for tp in tp_range:
        for sl in sl_range:
            for x in x_range:
                iteration += 1
                paper_trade.take_profit = tp
                paper_trade.stop_loss = sl
                paper_trade.x_prices = x
                current_profit = run_backtest_pt(paper_trade, market_data)

                print(f"Iteration {iteration}/{total_iterations}: TP={tp}, SL={sl}, X={x}, Profit={current_profit}")

                if current_profit > best_profit:
                    best_profit = current_profit
                    best_tp = tp
                    best_sl = sl
                    best_x = x

                    print(f"New best profit found: {best_profit} with TP={best_tp}, SL={best_sl}, X={best_x}")

                # Store the result in the database
                OptimizationResult.objects.create(
                    paper_trade=paper_trade,
                    take_profit=tp,
                    stop_loss=sl,
                    profit=current_profit
                )

    # Update the paper_trade with the best parameters
    paper_trade.take_profit = best_tp
    paper_trade.stop_loss = best_sl
    paper_trade.x_prices = best_x
    paper_trade.save()

    return best_tp, best_sl, best_x, best_profit