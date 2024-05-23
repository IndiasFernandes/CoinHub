# models.py

from django.db import models
from django.utils import timezone

class Backtest(models.Model):
    exchange = models.ForeignKey('exchanges.Exchange', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=50)
    cash = models.DecimalField(max_digits=20, decimal_places=2)
    commission = models.DecimalField(max_digits=5, decimal_places=4)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.DurationField(blank=True, null=True)
    exposure_time_percent = models.FloatField(blank=True, null=True)
    equity_final = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    equity_peak = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    return_percent = models.FloatField(blank=True, null=True)
    annual_return_percent = models.FloatField(blank=True, null=True)
    max_drawdown_percent = models.FloatField(blank=True, null=True)
    sharpe_ratio = models.FloatField(blank=True, null=True)
    sortino_ratio = models.FloatField(blank=True, null=True)
    calmar_ratio = models.FloatField(blank=True, null=True)
    number_of_trades = models.IntegerField(blank=True, null=True)
    win_rate_percent = models.FloatField(blank=True, null=True)
    avg_trade_percent = models.FloatField(blank=True, null=True)
    profit_factor = models.FloatField(blank=True, null=True)
    sqn = models.FloatField(blank=True, null=True)
    graph_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    exchange = models.ForeignKey('exchanges.Exchange', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=50)
    cash = models.DecimalField(max_digits=20, decimal_places=2)
    commission = models.DecimalField(max_digits=5, decimal_places=4)
    atr_timeperiod = models.DecimalField(max_digits=10, decimal_places=2)
    atr_multiplier = models.DecimalField(max_digits=10, decimal_places=2)
    sharpe_ratio = models.FloatField(blank=True, null=True)
    return_percent = models.FloatField(blank=True, null=True)
    max_drawdown_percent = models.FloatField(blank=True, null=True)
    graph_link = models.URLField(blank=True, null=True)
    heat_map_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    exposure_time_percent = models.FloatField(blank=True, null=True)
    equity_final = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    equity_peak = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    annual_return_percent = models.FloatField(blank=True, null=True)
    number_of_trades = models.IntegerField(blank=True, null=True)
    win_rate_percent = models.FloatField(blank=True, null=True)
    avg_trade_percent = models.FloatField(blank=True, null=True)
    profit_factor = models.FloatField(blank=True, null=True)
    sortino_ratio = models.FloatField(blank=True, null=True)
    calmar_ratio = models.FloatField(blank=True, null=True)
    sqn = models.FloatField(blank=True, null=True)
    repetitions = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Optimization"
        verbose_name_plural = "Optimizations"

class PaperTrade(models.Model):
    name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class MarketData(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    def __str__(self):
        return self.symbol
