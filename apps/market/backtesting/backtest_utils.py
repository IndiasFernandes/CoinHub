import os
from datetime import datetime
from backtesting import Backtest as BT

from CoinHub import settings
from apps.exchanges.utils.utils import import_csv
from .strategy.SuperTrend_Strategy_Backtest import SuperTrendBacktest
from ..models import Backtest


def run_backtest(symbol, df, timeperiod, cash=100000, commission=.008, openbrowser=False):
    bt = BT(df, SuperTrendBacktest, cash=cash, commission=commission, exclusive_orders=True)
    main_path = os.path.join('static', 'backtest', 'backtest_results',
                             f'{symbol.replace("/", "_")}_{datetime.now().isoformat()}')
    bt_path = os.path.join(settings.BASE_DIR, main_path)
    stats = bt.run()
    bt.plot(open_browser=openbrowser, filename=bt_path)

    price_value, st_value = fetch_latest_values('backtest')
    save_backtest_instance(stats, symbol, cash, commission, timeperiod, main_path)

    return st_value, price_value


def fetch_latest_values(folder):
    price_path = os.path.join(settings.BASE_DIR, f'static/{folder}/last_price.csv')
    st_path = os.path.join(settings.BASE_DIR, f'static/{folder}/last_st.csv')

    price_value = float(import_csv(price_path)[0][0]) if os.path.exists(price_path) else 0
    st_value = float(import_csv(st_path)[0][0]) if os.path.exists(st_path) else 0

    return price_value, st_value


def save_backtest_instance(stats, symbol, cash, commission, timeperiod, main_path):
    if stats['# Trades'] > 1:
        Backtest.objects.create(
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
            graph_link=main_path + '.html',
            timeperiod=timeperiod
        )
