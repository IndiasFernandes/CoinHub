from django.db import models
from django.utils import timezone


class Backtest(models.Model):
    symbol = models.CharField(max_length=10)
    timeperiod = models.CharField(max_length=5)
    cash = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.DurationField()
    exposure_time_percent = models.FloatField()
    equity_final = models.DecimalField(max_digits=12, decimal_places=2)
    equity_peak = models.DecimalField(max_digits=12, decimal_places=2)
    return_percent = models.FloatField()
    annual_return_percent = models.FloatField()
    max_drawdown_percent = models.FloatField()
    sharpe_ratio = models.FloatField()
    sortino_ratio = models.FloatField()
    calmar_ratio = models.FloatField()
    number_of_trades = models.IntegerField()
    win_rate_percent = models.FloatField()
    avg_trade_percent = models.FloatField()
    profit_factor = models.FloatField()
    sqn = models.FloatField()
    graph_link = models.URLField(blank=True, null=True)  # Optional link to the graph
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    symbol = models.CharField(max_length=10)
    timeperiod = models.CharField(max_length=5)
    cash = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    atr_timeperiod = models.IntegerField()
    atr_multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    sharpe_ratio = models.FloatField()
    return_percent = models.FloatField()
    max_drawdown_percent = models.FloatField()
    graph_link = models.URLField(blank=True, null=True)  # Optional link to the graph
    heat_map_link = models.URLField(blank=True, null=True)  # Optional link to the heat map
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(blank=True, null=True)
    exposure_time_percent = models.FloatField()
    equity_final = models.DecimalField(max_digits=12, decimal_places=2)
    equity_peak = models.DecimalField(max_digits=12, decimal_places=2)
    annual_return_percent = models.FloatField()
    number_of_trades = models.IntegerField()
    win_rate_percent = models.FloatField()
    avg_trade_percent = models.FloatField()
    profit_factor = models.FloatField(blank=True, null=True)
    sharpe_ratio = models.FloatField()
    sortino_ratio = models.FloatField()
    calmar_ratio = models.FloatField()
    sqn = models.FloatField(blank=True, null=True)
    repetitions = models.IntegerField()

    class Meta:
        verbose_name = "Optimization"
        verbose_name_plural = "Optimizations"

    def __str__(self):
        return f"{self.symbol} ({self.timeperiod}) - Best Sharpe Ratio: {self.sharpe_ratio}"
