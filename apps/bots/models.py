from django.db import models
from django.contrib.auth.models import User
from apps.exchanges.models import Exchange, Market


class Strategy(models.Model):
    STRATEGY_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    STRATEGY_POSITION_CHOICES = [
        ('SHORT', 'Short'),
        ('LONG', 'Long'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    strategy_type = models.CharField(max_length=4, choices=STRATEGY_TYPE_CHOICES, default='BUY')
    position = models.CharField(max_length=5, choices=STRATEGY_POSITION_CHOICES, default='LONG')
    logic = models.TextField(help_text="Python code for the strategy logic")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Strategy"
        verbose_name_plural = "Strategies"

class Bot(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, blank=True, null=True)
    market = models.ForeignKey(Market, on_delete=models.SET_NULL, null=True, blank=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    max_drawdown_percentage = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    task_id = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f'{self.user.username} {self.exchange.name}'

class Trade(models.Model):
    TRADE_TYPES = (
        ('L', 'Long'),
        ('S', 'Short'),
    )
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    price = models.DecimalField(max_digits=15, decimal_places=5)
    fee = models.DecimalField(max_digits=15, decimal_places=5, default=0.0)  # Added fee field
    leverage = models.IntegerField(null=True, blank=True)  # Added leverage field, optional
    trade_type = models.CharField(max_length=1, choices=TRADE_TYPES, default='L')
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.bot.user.username} {self.timestamp}'
