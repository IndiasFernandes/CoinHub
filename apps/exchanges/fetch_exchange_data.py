import requests

# Define API endpoints for the exchanges and their respective markets
API_ENDPOINTS = {
    'hyperliquid': {
        'spot': 'https://api.hyperliquid.xyz/info'
    },
    'binance': {
        'spot': 'https://api.binance.com/api/v3/exchangeInfo',
        'futures': 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    },
    'coinbase': {
        'spot': 'https://api.exchange.coinbase.com/products'
    },
    'kraken': {
        'spot': 'https://api.kraken.com/0/public/AssetPairs'
    },
    'bitfinex': {
        'spot': 'https://api-pub.bitfinex.com/v2/tickers?symbols=ALL'
    },
    'okex': {
        'spot': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
        'futures': 'https://www.okx.com/api/v5/market/tickers?instType=FUTURES'
    }
}

# Function to fetch and parse data from HyperLiquid for a given market
def fetch_hyperliquid(market):
    response = requests.post(API_ENDPOINTS['hyperliquid'][market], json={"type": "allMids"})
    data = response.json()
    symbols = [f"{symbol}/{data[symbol]}" for symbol in data.keys()]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    return symbols, timeframes

# Function to fetch and parse data from Binance for a given market
def fetch_binance(market):
    response = requests.get(API_ENDPOINTS['binance'][market])
    data = response.json()
    symbols = [f"{symbol['baseAsset']}/{symbol['quoteAsset']}" for symbol in data['symbols']]
    timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    return symbols, timeframes

# Function to fetch and parse data from Coinbase for a given market
def fetch_coinbase(market):
    response = requests.get(API_ENDPOINTS['coinbase'][market])
    data = response.json()
    symbols = [f"{product['base_currency']}/{product['quote_currency']}" for product in data]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '1d', '1w', '1M']
    return symbols, timeframes

# Function to fetch and parse data from Kraken for a given market
def fetch_kraken(market):
    response = requests.get(API_ENDPOINTS['kraken'][market])
    data = response.json()
    symbols = [f"{pair['base']}/{pair['quote']}" for pair in data['result'].values()]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    return symbols, timeframes

# Function to fetch and parse data from Bitfinex for a given market
def fetch_bitfinex(market):
    response = requests.get(API_ENDPOINTS['bitfinex'][market])
    data = response.json()
    symbols = [f"{item[0]}" for item in data]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    return symbols, timeframes

# Function to fetch and parse data from OKEx for a given market
def fetch_okex(market):
    response = requests.get(API_ENDPOINTS['okex'][market])
    data = response.json()
    symbols = [item['instId'] for item in data['data']]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    return symbols, timeframes

def fetch_all_exchange_data():
    exchanges = {
        'hyperliquid': {market: fetch_hyperliquid(market) for market in API_ENDPOINTS['hyperliquid']},
        'binance': {market: fetch_binance(market) for market in API_ENDPOINTS['binance']},
        'coinbase': {market: fetch_coinbase(market) for market in API_ENDPOINTS['coinbase']},
        'kraken': {market: fetch_kraken(market) for market in API_ENDPOINTS['kraken']},
        'bitfinex': {market: fetch_bitfinex(market) for market in API_ENDPOINTS['bitfinex']},
        'okex': {market: fetch_okex(market) for market in API_ENDPOINTS['okex']}
    }
    return exchanges

if __name__ == "__main__":
    exchange_data = fetch_all_exchange_data()
    for exchange, markets in exchange_data.items():
        print(f"{exchange}:")
        for market, (symbols, timeframes) in markets.items():
            print(f"  Market: {market}")
            print(f"    Symbols: {symbols}")
            print(f"    Timeframes: {timeframes}")
