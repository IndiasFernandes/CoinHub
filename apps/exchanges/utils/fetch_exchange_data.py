import requests
from exchanges.models import Exchange, Coin, Market
from django.core.management.base import BaseCommand

API_ENDPOINTS = {
    'hyperliquid': 'https://api.hyperliquid.exchange/v1/market/symbols',
    'binance': 'https://api.binance.com/api/v3/exchangeInfo'
}

def fetch_hyperliquid():
    response = requests.get(API_ENDPOINTS['hyperliquid'])
    data = response.json()
    symbols = [f"{symbol['baseAsset']}/{symbol['quoteAsset']}" for symbol in data['symbols']]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    return symbols, timeframes

def fetch_binance():
    response = requests.get(API_ENDPOINTS['binance'])
    data = response.json()
    symbols = [f"{symbol['baseAsset']}/{symbol['quoteAsset']}" for symbol in data['symbols']]
    timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    return symbols, timeframes

def update_exchange_data():
    exchanges_data = {
        'hyperliquid': fetch_hyperliquid(),
        'binance': fetch_binance()
    }

    for exchange_name, (symbols, timeframes) in exchanges_data.items():
        exchange, created = Exchange.objects.get_or_create(name=exchange_name.capitalize())

        # Delete existing symbols and markets for this exchange
        Market.objects.filter(exchange=exchange).delete()
        Coin.objects.filter(markets__exchange=exchange).delete()

        # Add new symbols and markets
        for symbol in symbols:
            coin, created = Coin.objects.get_or_create(symbol=symbol)
            market, created = Market.objects.get_or_create(exchange=exchange, market_type='spot')
            market.coins.add(coin)

class Command(BaseCommand):
    help = 'Fetches and updates exchange data'

    def handle(self, *args, **kwargs):
        update_exchange_data()
        self.stdout.write(self.style.SUCCESS('Successfully updated exchange data'))
