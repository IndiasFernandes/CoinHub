import os
from datetime import datetime
import pandas as pd
from backtesting import Backtest as BT
from backtesting.lib import plot_heatmaps

from CoinHub import settings
from apps.exchanges.utils.utils import import_csv
from .strategy.SuperTrend_Strategy_Optimize import SuperTrendOptimize
from ..models import Optimize


def run_optimization(symbol, interval, cash, commission, openbrowser, df, max_tries, atr_timeperiod_range, atr_multiplier_range):
    bt = BT(df, SuperTrendOptimize, cash=cash, commission=commission, exclusive_orders=True)

    stats, heatmap = bt.optimize(
        atr_timeperiod=atr_timeperiod_range,
        atr_multiplier=atr_multiplier_range,
        maximize='Sharpe Ratio',
        return_heatmap=True,
        max_tries=max_tries,
        method="skopt"
    )

    hm_main_path, bt_main_path, stats_path, run_path, dict_path = generate_paths(symbol, max_tries)
    bt.plot(open_browser=openbrowser, filename=bt_main_path)
    plot_heatmaps(heatmap, open_browser=openbrowser, filename=hm_main_path)

    save_best_parameters(stats, run_path)
    save_review(stats, symbol, interval, dict_path)
    save_stats(stats, stats_path)
    price_value, st_value = fetch_latest_values('optimize')
    save_optimization_instance(stats, symbol, interval, price_value, st_value, hm_main_path, bt_main_path, cash, commission, max_tries)

def generate_paths(symbol, max_tries):
    base_dir = 'static/optimize/optimize_results'
    timestamp = datetime.now().isoformat()
    hm_main_path = os.path.join(base_dir, f'{max_tries}_{symbol.replace("/", "_")}_{timestamp}_Heat_Map.html')
    bt_main_path = os.path.join(base_dir, f'{max_tries}_{symbol.replace("/", "_")}_{timestamp}_Backtest.html')
    stats_path = os.path.join(base_dir, f'{max_tries}_{symbol.replace("/", "_")}_{timestamp}_Statistics.txt')
    run_path = os.path.join(base_dir, f'{max_tries}_{symbol.replace("/", "_")}_{timestamp}_Best_Parameters.csv')
    dict_path = os.path.join(base_dir, 'Review.csv')
    return hm_main_path, bt_main_path, stats_path, run_path, dict_path

def save_best_parameters(stats, run_path):
    best_params = {
        "atr_timeperiod": float(stats["_strategy"].atr_timeperiod),
        "atr_multiplier": float(stats["_strategy"].atr_multiplier),
    }
    with open(run_path, 'w') as file:
        for key, value in best_params.items():
            file.write(f"{key}, {value}\n")

def save_review(stats, symbol, interval, dict_path):
    review_data = {
        "Coin": symbol,
        "Timeframe": interval,
        "Trades": str(stats["# Trades"]),
        "Sharp Ratio": str(stats["Sharpe Ratio"]),
        "Return": str(stats["Return [%]"]),
        "Max. Drawdown": str(stats["Max. Drawdown [%]"])
    }
    review_df = pd.DataFrame(review_data, index=[0])
    review_df.to_csv(dict_path, mode='a', index=False, header=not os.path.isfile(dict_path))

def save_stats(stats, stats_path):
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(stats.to_string())

def fetch_latest_values(folder):
    price_path = os.path.join(settings.BASE_DIR, f'static/{folder}/last_price.csv')
    st_path = os.path.join(settings.BASE_DIR, f'static/{folder}/last_st.csv')

    price_value = float(import_csv(price_path)[0][0]) if os.path.exists(price_path) else 0
    st_value = float(import_csv(st_path)[0][0]) if os.path.exists(st_path) else 0

    return price_value, st_value

def save_optimization_instance(stats, symbol, interval, price_value, st_value, hm_main_path, bt_main_path, cash, commission, max_tries):
    if stats['# Trades'] > 1:
        Optimize.objects.create(
            symbol=symbol,
            timeperiod=interval,
            atr_timeperiod=stats["_strategy"].atr_timeperiod,
            atr_multiplier=stats["_strategy"].atr_multiplier,
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
