from datetime import timedelta

from django.db import models
from django.utils import timezone

class Backtest(models.Model):
    exchange = models.ForeignKey('exchanges.Exchange', on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    timeframe = models.CharField(max_length=50, null=True, blank=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
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

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    exchange = models.ForeignKey('exchanges.Exchange', on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    timeframe = models.CharField(max_length=50, null=True, blank=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    atr_timeperiod = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    atr_multiplier = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    return_percent = models.FloatField(null=True, blank=True)
    max_drawdown_percent = models.FloatField(null=True, blank=True)
    graph_link = models.URLField(blank=True, null=True)
    heat_map_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
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
    max_tries = models.IntegerField(default=1, null=True, blank=True)  # Add this field

    class Meta:
        verbose_name = "Optimization"
        verbose_name_plural = "Optimizations"

class PaperTrade(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

class MarketData(models.Model):
    symbol = models.CharField(max_length=10, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.symbol
