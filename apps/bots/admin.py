from django.contrib import admin
from .models import Strategy, Bot, Trade

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('user', 'exchange', 'market', 'strategy', 'is_active')
    list_filter = ('user', 'exchange', 'strategy', 'is_active')

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('bot', 'market', 'volume', 'price', 'fee', 'leverage', 'trade_type', 'timestamp')
    list_filter = ('bot', 'timestamp', 'trade_type')