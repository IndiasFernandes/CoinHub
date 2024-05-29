# apps/market/backtesting/backtest_utils.py
import os
from decimal import Decimal
from datetime import datetime
from backtesting import Backtest as BT

from CoinHub import settings
from .strategy.SuperTrend_Strategy_Backtest import SuperTrendBacktest
from ..models import Backtest


def run_backtest(symbol, df, timeperiod, exchange, cash=100000, commission=.008, openbrowser=False):
    # Convert Decimal to float
    cash = float(cash) if isinstance(cash, Decimal) else cash
    commission = float(commission) if isinstance(commission, Decimal) else commission

    bt = BT(df, SuperTrendBacktest, cash=cash, commission=commission, exclusive_orders=True)
    main_path = os.path.join('static', 'backtest', 'backtest_results',
                             f'{symbol.replace("/", "_")}_{datetime.now().isoformat()}')
    bt_path = os.path.join(settings.BASE_DIR, main_path)
    stats = bt.run()

    # Access latest values from the strategy instance
    st_value = bt._strategy.st_value
    price_value = bt._strategy.price

    bt.plot(open_browser=openbrowser, filename=bt_path)

    save_backtest_instance(exchange, stats, symbol, cash, commission, timeperiod, main_path)

    return st_value, price_value


def save_backtest_instance(exchange, stats, symbol, cash, commission, timeperiod, main_path):
    if stats['# Trades'] > 1:
        Backtest.objects.create(
            exchange=exchange,
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
            timeframe=timeperiod
        )
