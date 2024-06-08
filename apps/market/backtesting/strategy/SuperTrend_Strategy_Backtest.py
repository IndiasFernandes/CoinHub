from backtesting import Strategy
from CoinHub import settings
from apps.exchanges.utils.utils import import_csv
from apps.market.backtesting.strategy.SuperTrend import get_supertrend
from apps.market.models import Optimize
import os
import csv
from django.db.models import Q


class SuperTrendBacktest(Strategy):
    atr_timeperiod = None
    atr_multiplier = None
    last_st=None
    last_price=None



    def init(self):

        self.st, self.s_upt, self.st_dt = self.I(get_supertrend, self.data.df['High'], self.data.df['Low'], self.data.df['Close'], self.atr_timeperiod,
                                                 self.atr_multiplier, self.atr_timeperiod)

        self.st = self.st[1:]
        self.s_upt = self.s_upt[1:]
        self.st_dt = self.st_dt[1:]

    def next(self):
        previous_price = self.data.Close[-2]
        price = self.data.Close[-1]

        # Trade logic
        if self.st[-2] > previous_price and self.st[-1] < price:
            self.position.close()
            self.buy(size=0.99)
        elif self.st[-2] < previous_price and self.st[-1] > price:
            self.position.close()
            self.sell(size=0.99)


        self.last_st = self.st[-1]
        self.last_price = price


