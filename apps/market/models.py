from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.exchanges.models import Exchange

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

    class Meta:
        verbose_name = "Backtest"
        verbose_name_plural = "Backtests"

class Optimize(models.Model):
    exchange = models.CharField(max_length=50, null=True, blank=True)
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
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # Could be 'long', 'short', etc.
    timeframe = models.CharField(max_length=50)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=2)
    update_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    trading_enabled = models.BooleanField(default=True)  # Toggle for trading on/off

    def __str__(self):
        return self.name

class MarketData(models.Model):
    paper_trade = models.ForeignKey(PaperTrade, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    super_trend_status = models.CharField(max_length=10)  # 'long', 'short', or 'neutral'
    trade_indicator = models.BooleanField(default=False)

    def check_trade(self):
        # Add logic to determine the trade indicator based on last and current super_trend_status
        # This method should be called every time new data is saved and update `trade_indicator` accordingly
        last_data = MarketData.objects.filter(paper_trade=self.paper_trade).order_by('-timestamp').first()
        if last_data:
            # Example logic, should be adjusted as per actual trading algorithm
            if (last_data.super_trend_status == 'long' and last_data.price < self.price) or \
               (last_data.super_trend_status == 'short' and last_data.price > self.price):
                self.trade_indicator = True
            self.save()

    def __str__(self):
        return f"{self.paper_trade.name} - {self.timestamp} - {self.price} - {self.trade_indicator}"