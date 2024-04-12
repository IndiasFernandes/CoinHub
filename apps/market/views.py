import csv
import os
from datetime import datetime

from .models import Backtest
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


cash = 100000
commission = .008
openbrowser = True

def backtest(symbol, cash, commission, openbrowser, df):

    print('Backtesting - Bot Func ...')

    bt = BT(df,
                  SuperTrendBacktest,
                  cash=cash,
                  commission=commission,
                  exclusive_orders=True)

    stats = bt.run()
    print(stats)
    bt.plot(open_browser=openbrowser)

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
        profit_factor=stats['Profit Factor'],
        sqn=stats['SQN'],
        created_at=datetime.now()
    )
    backtest_instance.save()

    return st_value, price_value


# def optimize(self, symbol, interval, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range,
#              atr_multiplier_range):
#     print('Optimizing - Bot Func ...')
#
#     bt = Backtest(df,
#                   SuperTrendOptimize,
#                   cash=cash,
#                   commission=commission,
#                   exclusive_orders=True)
#
#     stats, heatmap = bt.optimize(
#         atr_timeperiod=atr_timeperiod_range,
#         atr_multiplier=atr_multiplier_range,
#         maximize='Sharpe Ratio',
#         return_heatmap=True,
#         max_tries=max_tries,
#         method="skopt")
#
#     # Output Paths
#     hm_path = 'export/optimize/' + str(max_tries) + '_' + symbol + '_' + interval + '_Heat_Map.html'
#     bt_path = 'export/optimize/' + str(max_tries) + '_' + symbol + '_' + interval + '_Backtesting.html'
#     stats_path = 'export/optimize/' + str(max_tries) + '_' + symbol + '_' + interval + '_Statistics.txt'
#     run_path = 'export/optimize/' + str(max_tries) + '_' + symbol + '_' + interval + '_Best_Parameters.csv'
#     dict_path = 'export/optimize/' + str(max_tries) + '_' + 'Review.csv'
#
#     # Plotting
#     bt.plot(open_browser=openbrowser, filename=bt_path)
#     plot_heatmaps(heatmap, open_browser=openbrowser, filename=hm_path)
#
#     # Dictionary with Best Parameters
#     bestParams = {
#         "atr_timeperiod": float(stats["_strategy"].atr_timeperiod),
#         "atr_multiplier": float(stats["_strategy"].atr_multiplier),
#     }
#
#     # create an instance of Optimize
#     optimize = Optimize()
#
#     # set the fields of the instance
#     optimize.symbol = symbol
#     optimize.timeperiod = interval
#     optimize.repetitions = max_tries
#     optimize.atr_timeperiod = bestParams['atr_timeperiod']
#     optimize.atr_multiplier = bestParams['atr_multiplier']
#     optimize.created_at = datetime.now()
#
#     # save the instance to the database
#     optimize.save()
#
#     # Save Best Parameters
#     with open(run_path, 'w') as file:
#         for key in bestParams.keys():
#             file.write("%s, %s\n" % (key, bestParams[key]))
#
#     # Dictionary with Review
#     reviewD = {
#         "Coin": symbol,
#         "Timeframe": interval,
#         "Trades": str(stats["# Trades"]),
#         "Sharp Ratio": str(stats["Sharpe Ratio"]),
#         "Return": str(stats["Return [%]"]),
#         "Max. Drawdown": str(stats["Max. Drawdown [%]"])
#     }
#
#     # Save Review
#     reviewD = pd.DataFrame(reviewD, index=[0])
#     if os.path.isfile(dict_path):
#         reviewD.to_csv(dict_path, mode='a', index=False, header=False)  # save the file
#     else:
#         reviewD.to_csv(dict_path, mode='a', index=False)
#
#     # Save Statistics
#     with open(stats_path, 'w', encoding='utf-8') as f:
#         f.write(stats.to_string())
#
#     data = import_csv('export/last_price.csv')
#
#     for items in data:
#         for item in items:
#             price_value = float(item)
#
#     data = import_csv('export/last_st.csv')
#
#     for items in data:
#         for item in items:
#             st_value = float(item)
#
#     # Output
#     thisdict = {
#         "Net Profit": round(stats["Return [%]"], 3),
#         "Total Closed Trades": stats["# Trades"],
#         "Percent Profitable": stats["Win Rate [%]"],
#         "Profit Factor": stats["Profit Factor"],
#         "Max. Drawdown": stats["Max. Drawdown [%]"],
#         "St Value": st_value
#     }
#
#     df_dict = pd.DataFrame(thisdict, index=[0])
#
#     dict_path = 'export/backtest_results/' + symbol + '.csv'
#
#     if os.path.isfile(dict_path):
#         df_dict.to_csv(dict_path, mode='a', index=False, header=False)  # save the file
#     else:
#         df_dict.to_csv(dict_path, mode='a', index=False)


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
    st, price = backtest(symbol, cash, commission, openbrowser, df)

    if price > st:
        dict[timeperiod] = 'Long'
    elif price < st:
        dict[timeperiod] = 'Short'

    return {"symbol": symbol, "timeframe": timeperiod, "file": output_path}

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



def backtest_list(request):
    backtests = Backtest.objects.all()  # Fetch all backtest records
    return render(request, 'pages/market/backtests_list.html', {'backtests': backtests, 'current_section': 'market'})

def backtest_detail(request, backtest_id):
    backtest = Backtest.objects.get(id=backtest_id)

    return render(request, 'pages/market/backtest_detail.html', {'backtest': backtest, 'current_section': 'market'})