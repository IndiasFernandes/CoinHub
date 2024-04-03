# bots/models.py

from django.db import models
from django.contrib.auth.models import User
from exchanges.models import Exchange, Market

class Strategy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.SET_NULL, null=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)

class Trade(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    price = models.DecimalField(max_digits=15, decimal_places=5)
    timestamp = models.DateTimeField(auto_now_add=True)
