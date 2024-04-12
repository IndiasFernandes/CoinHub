from django.db import models

class Backtest(models.Model):
    symbol = models.CharField(max_length=255)
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    symbol = models.CharField(max_length=255)
    timeperiod = models.CharField(max_length=255)
    repetitions = models.IntegerField()
    atr_timeperiod = models.FloatField()
    atr_multiplier = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        verbose_name = "Optimize"
        verbose_name_plural = "Optimizes"