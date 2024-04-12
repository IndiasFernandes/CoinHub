from django.contrib import admin
from .models import Exchange, Market, Coin, HistoricalData

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url')

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('symbol',)

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'market_type', 'coins_list')
    list_filter = ('exchange', 'coins')

    def coins_list(self, obj):
        return ", ".join([coin.symbol for coin in obj.coins.all()])
    coins_list.short_description = "Coins"

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ('market', 'open_price', 'close_price', 'high_price', 'low_price', 'volume', 'timestamp')
    list_filter = ('market', 'timestamp')
