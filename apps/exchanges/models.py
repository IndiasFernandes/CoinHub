from django.db import models

class Exchange(models.Model):
    id_char = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    api_url = models.URLField(null=True, blank=True)
    api_key = models.CharField(max_length=100, null=True, blank=True)
    secret_key = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Coin(models.Model):
    symbol = models.CharField(max_length=10, null=True, blank=True)  # Example: BTC, ETH

    def __str__(self):
        return self.symbol

class Market(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, null=True, blank=True)
    market_type = models.CharField(max_length=20, default='spot')  # Add a field for market type
    coins = models.ManyToManyField(Coin, related_name='markets', blank=True)

    def __str__(self):
        return f"{self.exchange.name} - {self.market_type}"

class HistoricalData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, null=True, blank=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    close_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    high_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    low_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    volume = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        coins_symbols = ", ".join([coin.symbol for coin in self.market.coins.all()])
        return f'Market: {self.market.exchange.name} - {self.market.market_type}, Coins: {coins_symbols}, Timestamp: {self.timestamp}'

    class Meta:
        verbose_name = "Historical Data"
        verbose_name_plural = "Historical Data"

class ExchangeInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    account_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_margin_used = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_net_position = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_raw_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    withdrawable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Exchange Information"
