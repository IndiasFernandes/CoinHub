import os
from decimal import Decimal
from datetime import datetime
from backtesting import Backtest as BT
from CoinHub import settings
from apps.exchanges.utils.utils import import_csv
from .strategy.SuperTrend_Strategy_Backtest import SuperTrendBacktest
from ..models import Backtest


def run_backtest(symbol, df, timeperiod, exchange, cash=10000000, commission=.008, openbrowser=False, atr_timeperiod=1.95, atr_multiplier=2.79):
    # Convert Decimal to float
    cash = float(cash) if isinstance(cash, Decimal) else cash
    commission = float(commission) if isinstance(commission, Decimal) else commission

    backtest_instance = Backtest.objects.create(
        exchange=exchange,
        symbol=symbol,
        cash=cash,
        commission=commission,
        timeframe=timeperiod,
        created_at=datetime.now()
    )

    bt = BT(df, SuperTrendBacktest, cash=cash, commission=commission, exclusive_orders=True)

    main_path = os.path.join('static', 'backtest', 'backtest_results',
                             f'{symbol.replace("/", "_")}_{datetime.now().isoformat()}')
    bt_path = os.path.join(settings.BASE_DIR, main_path)

    stats = bt.run(atr_timeperiod=atr_timeperiod, atr_multiplier=atr_multiplier)
    st_value = stats._strategy.last_st
    price_value = stats._strategy.last_price

    bt.plot(open_browser=openbrowser, filename=bt_path)

    save_backtest_instance(backtest_instance, stats, st_value, price_value, main_path)

    return st_value, price_value


def save_backtest_instance(backtest_instance, stats, st_value, price_value, main_path):
    if stats['# Trades'] > 1:
        backtest_instance.start_date = stats['_trades'].iloc[0]['EntryTime'] if not stats['_trades'].empty else None
        backtest_instance.end_date = stats['_trades'].iloc[-1]['ExitTime'] if not stats['_trades'].empty else None
        backtest_instance.duration = stats['Duration']
        backtest_instance.exposure_time_percent = stats['Exposure Time [%]']
        backtest_instance.equity_final = stats['Equity Final [$]']
        backtest_instance.equity_peak = stats['Equity Peak [$]']
        backtest_instance.return_percent = stats['Return [%]']
        backtest_instance.annual_return_percent = stats['Return (Ann.) [%]']
        backtest_instance.max_drawdown_percent = stats['Max. Drawdown [%]']
        backtest_instance.sharpe_ratio = stats['Sharpe Ratio']
        backtest_instance.sortino_ratio = stats['Sortino Ratio']
        backtest_instance.calmar_ratio = stats['Calmar Ratio']
        backtest_instance.number_of_trades = stats['# Trades']
        backtest_instance.win_rate_percent = stats['Win Rate [%]']
        backtest_instance.avg_trade_percent = stats['Avg. Trade [%]']
        backtest_instance.sqn = stats['SQN']
        backtest_instance.graph_link = main_path + '.html'
        backtest_instance.last_st_value = st_value
        backtest_instance.last_price_value = price_value
        backtest_instance.save()

