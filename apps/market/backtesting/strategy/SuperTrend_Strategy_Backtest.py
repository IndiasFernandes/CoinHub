# apps/market/backtesting/strategy/SuperTrend_Strategy_Backtest.py
from backtesting import Strategy
from CoinHub import settings
from apps.exchanges.utils.utils import import_csv
from apps.market.backtesting.strategy.SuperTrend import get_supertrend
import os

class SuperTrendBacktest(Strategy):
    atr_timeperiod = 0.537
    atr_multiplier = 0.79
    atr_method = True

    def init(self):
        path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_symbol.csv')
        symbol = import_csv(path)[0][0]
        path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_timeperiod.csv')
        timeperiod = import_csv(path)[0][0]
        path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_multiplier.csv')
        self.atr_multiplier = float(import_csv(path)[0][0])
        path = os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_atr_timeperiod.csv')
        self.atr_timeperiod = float(import_csv(path)[0][0])

        print('Starting Backtest with the following parameters:')
        print('atr_timeperiod: ', self.atr_timeperiod)
        print('atr_multiplier: ', self.atr_multiplier)
        print('symbol: ', symbol)
        print('timeperiod: ', timeperiod)

        self.st, self.s_upt, self.st_dt = self.I(get_supertrend, self.data.df['High'], self.data.df['Low'], self.data.df['Close'], self.atr_timeperiod,
                                                 self.atr_multiplier, self.atr_timeperiod)

        self.st = self.st[1:]
        self.s_upt = self.s_upt[1:]
        self.st_dt = self.st_dt[1:]

        # Initialize latest values
        self.price = None
        self.st_value = None

    def next(self):
        previous_price = self.data.Close[-2]
        self.price = self.data.Close[-1]
        self.st_value = self.st[-1]

        # 0 - Long | 1 - Short | 2 - Both
        if self.st[-2] > previous_price and self.st[-1] < self.price:
            self.position.close()
            self.buy(size=0.99)
        elif self.st[-2] < previous_price and self.st[-1] > self.price:
            self.position.close()
            self.sell(size=0.99)
