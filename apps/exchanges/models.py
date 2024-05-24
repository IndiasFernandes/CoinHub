# exchanges/models.py

from django.db import models

class Exchange(models.Model):
    id_char = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    api_url = models.URLField()
    api_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)


    def __str__(self):
        return self.name

class Coin(models.Model):
    symbol = models.CharField(max_length=10)  # Example: BTC, ETH

    def __str__(self):
        return self.symbol

class Market(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    market_type = models.CharField(max_length=20, default='spot')  # Add a field for market type
    coins = models.ManyToManyField(Coin, related_name='markets')

    def __str__(self):
        return f"{self.exchange.name} - {self.market_type}"

class HistoricalData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    open_price = models.DecimalField(max_digits=15, decimal_places=5)
    close_price = models.DecimalField(max_digits=15, decimal_places=5)
    high_price = models.DecimalField(max_digits=15, decimal_places=5)
    low_price = models.DecimalField(max_digits=15, decimal_places=5)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    timestamp = models.DateTimeField()

    def __str__(self):
        # Assuming you want to list all related coins' symbols:
        coins_symbols = ", ".join([coin.symbol for coin in self.market.coins.all()])
        return f'Market: {self.market.exchange.name} - {self.market.market_type}, Coins: {coins_symbols}, Timestamp: {self.timestamp}'

    class Meta:
        verbose_name = "Historical Data"
        verbose_name_plural = "Historical Data"

class ExchangeInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_margin_used = models.DecimalField(max_digits=10, decimal_places=2)
    total_net_position = models.DecimalField(max_digits=10, decimal_places=2)
    total_raw_usd = models.DecimalField(max_digits=10, decimal_places=2)
    withdrawable = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Exchange Information"


