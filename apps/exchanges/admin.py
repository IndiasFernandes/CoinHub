from django.contrib import admin
from .models import Exchange, Market, HistoricalData

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url')

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'symbol')
    list_filter = ('exchange',)

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ('market', 'open_price', 'close_price', 'high_price', 'low_price', 'volume', 'timestamp')
    list_filter = ('market', 'timestamp')