from django.contrib.auth.models import User
from apps.exchanges.models import Exchange, Market
from django.db import models
from apps.market.models import Optimize
from django.utils import timezone

class BotEvaluation(models.Model):
    st = models.FloatField(null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    optimize = models.ForeignKey(Optimize, on_delete=models.CASCADE, null=True, blank=True)
    current_price = models.FloatField(null=True, blank=True)
    st_higher = models.BooleanField(default=False)
    st_lower = models.BooleanField(default=False)
    percentage_difference = models.FloatField(null=True, blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"{self.optimize.symbol} Evaluated on {self.evaluated_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Strategy(models.Model):
    STRATEGY_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    STRATEGY_POSITION_CHOICES = [
        ('SHORT', 'Short'),
        ('LONG', 'Long'),
    ]

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    strategy_type = models.CharField(max_length=4, choices=STRATEGY_TYPE_CHOICES, default='BUY', null=True, blank=True)
    position = models.CharField(max_length=5, choices=STRATEGY_POSITION_CHOICES, default='LONG', null=True, blank=True)
    logic = models.TextField(help_text="Python code for the strategy logic", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Strategy"
        verbose_name_plural = "Strategies"

class Bot(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, blank=True, null=True)
    market = models.ForeignKey(Market, on_delete=models.SET_NULL, null=True, blank=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    max_drawdown_percentage = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    task_id = models.CharField(max_length=50, blank=True, null=True)
    current_price = models.FloatField(null=True, blank=True, help_text="Current price of the cryptocurrency.")
    st_value = models.FloatField(null=True, blank=True, help_text="SuperTrend value used for decision making.")
    stop_loss = models.FloatField(null=True, blank=True, help_text="Stop-loss percentage to minimize losses.")
    loop_interval = models.IntegerField(null=True, blank=True, help_text="Time in seconds between each trading loop.")

    def __str__(self):
        return f'{self.user.username} {self.exchange.name}'

class Trade(models.Model):
    TRADE_TYPES = (
        ('L', 'Long'),
        ('S', 'Short'),
    )
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    fee = models.DecimalField(max_digits=15, decimal_places=5, default=0.0, null=True, blank=True)
    leverage = models.IntegerField(null=True, blank=True)
    trade_type = models.CharField(max_length=1, choices=TRADE_TYPES, default='L', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.bot.user.username} {self.timestamp}'
