# exchanges/models.py

from django.db import models

class Exchange(models.Model):
    name = models.CharField(max_length=100)
    api_url = models.URLField()

class Market(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)  # Example: BTC/USD

class HistoricalData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    open_price = models.DecimalField(max_digits=15, decimal_places=5)
    close_price = models.DecimalField(max_digits=15, decimal_places=5)
    high_price = models.DecimalField(max_digits=15, decimal_places=5)
    low_price = models.DecimalField(max_digits=15, decimal_places=5)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    timestamp = models.DateTimeField()
