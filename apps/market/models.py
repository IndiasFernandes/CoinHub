from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.exchanges.models import Exchange, Coin


def default_start_date():
    return timezone.now() - timedelta(days=60)

class Backtest(models.Model):
    exchange = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    timeframe = models.CharField(max_length=50, null=True, blank=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    start_date = models.DateTimeField(default=default_start_date, null=True, blank=True)
    end_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    exposure_time_percent = models.FloatField(null=True, blank=True)
    equity_final = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    equity_peak = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    return_percent = models.FloatField(null=True, blank=True)
    annual_return_percent = models.FloatField(null=True, blank=True)
    max_drawdown_percent = models.FloatField(blank=True, null=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    sortino_ratio = models.FloatField(null=True, blank=True)
    calmar_ratio = models.FloatField(blank=True, null=True)
    number_of_trades = models.IntegerField(null=True, blank=True)
    win_rate_percent = models.FloatField(null=True, blank=True)
    avg_trade_percent = models.FloatField(blank=True, null=True)
    profit_factor = models.FloatField(blank=True, null=True)
    sqn = models.FloatField(blank=True, null=True)
    graph_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    openbrowser = models.BooleanField(default=False)  # Add this field
    end_price_value = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Add this field
    st_value = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Add this field

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    exchange = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    timeframe = models.CharField(max_length=50, null=True, blank=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    atr_timeperiod = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    atr_multiplier = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    return_percent = models.FloatField(null=True, blank=True)
    max_drawdown_percent = models.FloatField(null=True, blank=True)
    graph_link = models.URLField(blank=True, null=True)
    heat_map_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    start_date = models.DateTimeField(default=default_start_date, blank=True, null=True)
    end_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    exposure_time_percent = models.FloatField(null=True, blank=True)
    equity_final = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    equity_peak = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    annual_return_percent = models.FloatField(null=True, blank=True)
    number_of_trades = models.IntegerField(null=True, blank=True)
    win_rate_percent = models.FloatField(null=True, blank=True)
    avg_trade_percent = models.FloatField(blank=True, null=True)
    profit_factor = models.FloatField(blank=True, null=True)
    sortino_ratio = models.FloatField(null=True, blank=True)
    calmar_ratio = models.FloatField(null=True, blank=True)
    sqn = models.FloatField(blank=True, null=True)
    openbrowser = models.BooleanField(default=False)  # Add this field
    max_tries = models.IntegerField(default=10, null=True, blank=True)  # Add this field

    class Meta:
        verbose_name = "Optimization"
        verbose_name_plural = "Optimizations"


class PaperTrade(models.Model):
    name = models.CharField(max_length=100)
    exchange = models.CharField(max_length=50, null=True, blank=True)
    coin = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=50)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=2)
    cron_timeframe = models.DecimalField(max_digits=20, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    lookback_period = models.IntegerField(default=7)
    is_active = models.BooleanField(default=True)
    atr_timeperiod = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    atr_multiplier = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    strategy = models.CharField(max_length=100)
    take_profit = models.DecimalField(max_digits=6, decimal_places=3, default=1.5)  # Example default value
    stop_loss = models.DecimalField(max_digits=6, decimal_places=3, default=1.5)  # Example default value
    trading_fee = models.DecimalField(max_digits=6, decimal_places=4, default=0.01)  # Example default value
    initial_account = models.DecimalField(max_digits=10, decimal_places=2, default=100.0)
    x_prices = models.IntegerField(default=1)  # Number of prices (candles) above/below supertrend for trades

    def __str__(self):
        return self.name

class MarketData(models.Model):
    paper_trade = models.ForeignKey(PaperTrade, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    st = models.DecimalField(max_digits=20, decimal_places=6)
    super_trend_status = models.CharField(max_length=10)
    trade_indicator = models.BooleanField(default=False)
    trade_action = models.CharField(max_length=10, blank=True, null=True)  # 'buy', 'sell', 'short', 'cover'
    profit = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    def __str__(self):
        return f"{self.paper_trade.name} - {self.timestamp} - {self.price} - {self.trade_indicator}"

    def check_trade(self, x_multiplier, fee):
        last_data = MarketData.objects.filter(paper_trade=self.paper_trade).order_by('-timestamp').first()
        if last_data:
            if last_data.trade_action in ['buy', 'short']:
                # Close the trade
                if (last_data.trade_action == 'buy' and self.price < last_data.st) or \
                   (last_data.trade_action == 'short' and self.price > last_data.st):
                    self.trade_indicator = False
                    self.trade_action = 'sell' if last_data.trade_action == 'buy' else 'cover'
                    profit = (self.price - last_data.price) if self.trade_action == 'sell' else (last_data.price - self.price)
                    self.profit = profit - (fee * profit)
                else:
                    self.trade_indicator = True
            else:
                # Open a new trade
                if self.price > self.st * x_multiplier:
                    self.trade_action = 'buy'
                    self.trade_indicator = True
                elif self.price < self.st * (1 / x_multiplier):
                    self.trade_action = 'short'
                    self.trade_indicator = True
            self.save()


from django.db import models

class OptimizationResult(models.Model):
    paper_trade = models.ForeignKey(PaperTrade, on_delete=models.CASCADE)
    take_profit = models.DecimalField(max_digits=5, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=5, decimal_places=2)
    profit = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.paper_trade.coin} - TP: {self.take_profit} SL: {self.stop_loss} Profit: {self.profit}"
