import csv
import os
from datetime import datetime
from urllib import request

import numpy as np
from backtesting.lib import plot_heatmaps

from .backtesting.strategy.SuperTrend_Strategy_Optimize import SuperTrendOptimize
from .models import Backtest, Optimize
import pandas as pd
from backtesting import Backtest as BT
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from apps.exchanges.models import DownloadDataForm
from apps.exchanges.utils.hyperliquid.download_data import initialize_exchange, download_data, heikin_ashi
from apps.exchanges.utils.utils import import_csv
from apps.market.backtesting.strategy.SuperTrend_Strategy_Backtest import SuperTrendBacktest

# BACKTESTING Settings

cash = 10000
commission = .008
openbrowser = False

# Optimization Settings
max_tries = 25
atr_timeperiod_range = np.arange(0, 3, 0.2)
atr_multiplier_range = np.arange(0, 3, 0.2)

def backtest(symbol,  df, timeperiod, cash=100000, commission=.008, openbrowser=False):


    print('Backtesting - Bot Func ...')

    bt = BT(df,
                  SuperTrendBacktest,
                  cash=cash,
                  commission=commission,
                  exclusive_orders=True)

    main_path = os.path.join('static', 'backtest', 'backtest_results', f'{symbol.replace("/", "_")}{str(datetime.now()).replace(" ", "_")}' )
    bt_path = os.path.join(settings.BASE_DIR, main_path)
    stats = bt.run()
    print(stats)
    bt.plot(open_browser=openbrowser, filename=bt_path)

    path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'last_price.csv')
    data = import_csv(path)

    for items in data:
        for item in items:
            price_value = float(item)

    path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'last_st.csv')

    data = import_csv(path)

    for items in data:
        for item in items:
            st_value = float(item)

    backtest_instance = Backtest(
        symbol=symbol,
        cash=cash,
        commission=commission,
        start_date=stats['_trades'].iloc[0]['EntryTime'] if not stats['_trades'].empty else None,
        end_date=stats['_trades'].iloc[-1]['ExitTime'] if not stats['_trades'].empty else None,
        duration=stats['Duration'],
        exposure_time_percent=stats['Exposure Time [%]'],
        equity_final=stats['Equity Final [$]'],
        equity_peak=stats['Equity Peak [$]'],
        return_percent=stats['Return [%]'],
        annual_return_percent=stats['Return (Ann.) [%]'],
        max_drawdown_percent=stats['Max. Drawdown [%]'],
        sharpe_ratio=stats['Sharpe Ratio'],
        sortino_ratio=stats['Sortino Ratio'],
        calmar_ratio=stats['Calmar Ratio'],
        number_of_trades=stats['# Trades'],
        win_rate_percent=stats['Win Rate [%]'],
        avg_trade_percent=stats['Avg. Trade [%]'],
        sqn=stats['SQN'],
        created_at=datetime.now(),
        graph_link=main_path+'.html',
        timeperiod=timeperiod
    )
    backtest_instance.save()

    return st_value, price_value



def optimize(symbol, interval, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range,
             atr_multiplier_range):
    print('Optimizing - Bot Func ...')

    bt = BT(df,
                  SuperTrendOptimize,
                  cash=cash,
                  commission=commission,
                  exclusive_orders=True)

    stats, heatmap = bt.optimize(
        atr_timeperiod=atr_timeperiod_range,
        atr_multiplier=atr_multiplier_range,
        maximize='Sharpe Ratio',
        return_heatmap=True,
        max_tries=max_tries,
        method="skopt")

    # Output Paths
    hm_main_path = os.path.join('static', 'optimize', 'optimize_results',
                             f'{max_tries}_{symbol.replace("/", "_")}_{str(datetime.now()).replace(" ", "_")}_Heat_Map.html')
    bt_main_path = os.path.join('static', 'optimize', 'optimize_results', f'{max_tries}_{symbol.replace("/", "_")}_{str(datetime.now()).replace(" ", "_")}_Backtest.html')
    hm_path = os.path.join(settings.BASE_DIR, hm_main_path)
    bt_path = os.path.join(settings.BASE_DIR, bt_main_path)
    stats_path = os.path.join(settings.BASE_DIR, 'static', 'optimize', 'optimize_results', f'{max_tries}_{symbol.replace("/", "_")}_{str(datetime.now()).replace(" ", "_")}_Statistics.txt')
    run_path = os.path.join(settings.BASE_DIR, 'static', 'optimize', 'optimize_results', f'{max_tries}_{symbol.replace("/", "_")}_{str(datetime.now()).replace(" ", "_")}_Best_Parameters.csv')
    dict_path = os.path.join(settings.BASE_DIR, 'static', 'optimize', 'optimize_results', 'Review.csv')

    # Plotting
    bt.plot(open_browser=openbrowser, filename=bt_path)
    plot_heatmaps(heatmap, open_browser=openbrowser, filename=hm_path)

    # Dictionary with Best Parameters
    bestParams = {
        "atr_timeperiod": float(stats["_strategy"].atr_timeperiod),
        "atr_multiplier": float(stats["_strategy"].atr_multiplier),
    }
    print(stats)


    # Save Best Parameters
    with open(run_path, 'w') as file:
        for key in bestParams.keys():
            file.write("%s, %s\n" % (key, bestParams[key]))

    # Dictionary with Review
    reviewD = {
        "Coin": symbol,
        "Timeframe": interval,
        "Trades": str(stats["# Trades"]),
        "Sharp Ratio": str(stats["Sharpe Ratio"]),
        "Return": str(stats["Return [%]"]),
        "Max. Drawdown": str(stats["Max. Drawdown [%]"])
    }

    # Save Review
    reviewD = pd.DataFrame(reviewD, index=[0])
    if os.path.isfile(dict_path):
        reviewD.to_csv(dict_path, mode='a', index=False, header=False)  # save the file
    else:
        reviewD.to_csv(dict_path, mode='a', index=False)

    # Save Statistics
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(stats.to_string())

    data_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'last_price.csv')
    data = import_csv(data_path)

    for items in data:
        for item in items:
            price_value = float(item)

    data_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'last_st.csv')
    data = import_csv(data_path)

    for items in data:
        for item in items:
            st_value = float(item)

    optimization_instance = Optimize(
        symbol=symbol,
        timeperiod=interval,
        atr_timeperiod=bestParams['atr_timeperiod'],
        atr_multiplier=bestParams['atr_multiplier'],
        return_percent=stats['Return [%]'],
        max_drawdown_percent=stats['Max. Drawdown [%]'],
        start_date=stats['_trades'].iloc[0]['EntryTime'] if not stats['_trades'].empty else None,
        end_date=stats['_trades'].iloc[-1]['ExitTime'] if not stats['_trades'].empty else None,
        duration=stats['Duration'],
        exposure_time_percent=stats['Exposure Time [%]'],
        equity_final=stats['Equity Final [$]'],
        annual_return_percent=stats['Return (Ann.) [%]'],
        sharpe_ratio=stats['Sharpe Ratio'],
        sortino_ratio=stats['Sortino Ratio'],
        calmar_ratio=stats['Calmar Ratio'],
        number_of_trades=stats['# Trades'],
        win_rate_percent=stats['Win Rate [%]'],
        avg_trade_percent=stats['Avg. Trade [%]'],
        sqn=stats['SQN'],
        created_at=datetime.now(),
        graph_link=bt_main_path,
        heat_map_link=hm_main_path,
        repetitions=max_tries,
        cash=cash,
        commission=commission,
        equity_peak=stats['Equity Peak [$]'],
    )
    optimization_instance.save()

    # If not a POST request, show the optimization form
    return


def perform_backtest(df, symbol, timeperiod):

    # Save Heikin Ashi to static folder
    output_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_symbol.csv')
    with open(output_path, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([symbol])

    output_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_timeperiod.csv')

    with open(output_path, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timeperiod])

    df_ha = heikin_ashi(df.reset_index())
    df_ha.set_index('Timestamp', inplace=True)
    st, price = backtest(symbol, df, timeperiod)
    # if price > st:
    #     dict[timeperiod] = 'Long'
    # elif price < st:
    #     dict[timeperiod] = 'Short'

    return {"symbol": symbol, "timeframe": timeperiod, "file": output_path, "st": st, "price": price}

def run_backtest(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            symbols = form.cleaned_data['symbol']
            timeperiods = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            exchange_id = form.cleaned_data['exchange_id']
            exchange = initialize_exchange(exchange_id, api_key='your_api_key', secret='your_secret')

            results = []
            for symbol in symbols:
                for timeperiod in timeperiods:
                    df = download_data([symbol], [timeperiod], start_date, end_date, exchange)
                    print(df)
                    result = perform_backtest(df, symbol, timeperiod)
                    results.append(result)

            messages.success(request, "Backtest completed successfully.")
            return JsonResponse({'results': results})
        else:
            messages.error(request, "Form data is invalid.")
    else:
        form = DownloadDataForm()
    return render(request, 'pages/market/backtest_form.html', {'form': form, 'current_section': 'market'})

def perform_optimization(df, symbol, timeperiod):

        # Save Heikin Ashi to static folder
        output_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_optimize_symbol.csv')
        with open(output_path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([symbol])

        output_path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_optimize_timeperiod.csv')

        with open(output_path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timeperiod])

        optimize(symbol, timeperiod, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range,
             atr_multiplier_range)

        return {"symbol": symbol, "timeframe": timeperiod, "file": output_path}

def run_optimization(request):
    if request.method == 'POST':
        form = DownloadDataForm(request.POST)
        if form.is_valid():
            symbols = form.cleaned_data['symbol']
            timeperiods = form.cleaned_data['timeframe']
            start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
            end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
            exchange_id = form.cleaned_data['exchange_id']
            exchange = initialize_exchange(exchange_id, api_key='your_api_key', secret='your_secret')

            results = []
            for symbol in symbols:
                for timeperiod in timeperiods:
                    df = download_data([symbol], [timeperiod], start_date, end_date, exchange)
                    print(df)
                    result = perform_optimization(df, symbol, timeperiod)
                    results.append(result)

            messages.success(request, "Optimization completed successfully.")
            return JsonResponse({'results': results})
        else:
            messages.error(request, "Form data is invalid.")
    else:
        form = DownloadDataForm()
    return render(request, 'pages/market/optimize_form.html', {'form': form, 'current_section': 'market'})


def backtest_list(request):
    backtests = Backtest.objects.all()  # Fetch all backtest records
    return render(request, 'pages/market/backtests_list.html', {'backtests': backtests, 'current_section': 'market'})

def backtest_detail(request, backtest_id):
    backtest = Backtest.objects.get(id=backtest_id)

    return render(request, 'pages/market/backtest_detail.html', {'backtest': backtest, 'current_section': 'market'})

def optimize_detail(request, optimize_id):
    optimization = Optimize.objects.get(id=optimize_id)

    return render(request, 'pages/market/optimize_detail.html', {'optimization': optimization, 'current_section': 'market'})

def optimize_list(request):
    optimization = Optimize.objects.all()  # Fetch all optimization results
    return render(request, 'pages/market/optimize_list.html', {'optimizations': optimization, 'current_section': 'market'})