import ccxt
import requests
import sys


def list_exchanges():
    return ccxt.exchanges


def fetch_exchange_data(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)()
    markets = exchange_class.load_markets()

    symbols = list(markets.keys())
    timeframes = exchange_class.timeframes if hasattr(exchange_class, 'timeframes') else []

    return symbols, timeframes


def fetch_all_exchange_data(selected_exchange):
    exchanges = [selected_exchange]
    exchange_data = {}

    for exchange_id in exchanges:
        try:
            symbols, timeframes = fetch_exchange_data(exchange_id)
            exchange_data[f"{exchange_id}_spot"] = (symbols, timeframes)
            # If the exchange supports futures, add futures data as well
            if exchange_id in ['binance', 'kraken']:  # Add other exchanges with futures markets here
                futures_exchange_id = f"{exchange_id}futures"
                futures_symbols, futures_timeframes = fetch_exchange_data(futures_exchange_id)
                exchange_data[f"{exchange_id}_futures"] = (futures_symbols, futures_timeframes)
        except Exception as e:
            print(f"Failed to fetch data for {exchange_id}: {str(e)}")

    return exchange_data


def update_exchange_data_file(exchanges_data):
    file_content = "EXCHANGES = {\n"
    for exchange_name, (symbols, timeframes) in exchanges_data.items():
        exchange_id_char, market_type = exchange_name.split('_')
        name = exchange_id_char.capitalize()
        market_name = "Spot" if market_type == "spot" else "Futures"

        file_content += f"    '{exchange_id_char}': {{\n"
        file_content += f"        'name': '{name}',\n"
        file_content += f"        'market': '{market_name}',\n"
        file_content += f"        'symbols': {symbols},\n"
        file_content += f"        'timeframes': {timeframes}\n"
        file_content += f"    }},\n"

    file_content += "}\n"

    with open('exchanges/exchange_data.py', 'w') as f:
        f.write(file_content)


def run_update(selected_exchange):
    exchange_data = fetch_all_exchange_data(selected_exchange)

    for exchange_name, (symbols, timeframes) in exchange_data.items():
        exchange_id_char, market_type = exchange_name.split('_')
        exchange, created = Exchange.objects.get_or_create(id_char=exchange_id_char,
                                                           defaults={'name': exchange_id_char.capitalize()})

        if not created:
            Market.objects.filter(exchange=exchange).delete()

        market = Market.objects.create(exchange=exchange, market_type=market_type)

        for symbol in symbols:
            coin, _ = Coin.objects.get_or_create(symbol=symbol)
            market.coins.add(coin)

        print(f'Successfully updated {exchange.name} - {market_type} market')

    update_exchange_data_file(exchange_data)
    print('exchange_data.py has been updated')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        available_exchanges = list_exchanges()
        selected_index = int(sys.argv[1]) - 1
        if selected_index < 0 or selected_index >= len(available_exchanges):
            print('Invalid selection.')
            sys.exit(1)

        selected_exchange = available_exchanges[selected_index]
        run_update(selected_exchange)
    else:
        available_exchanges = list_exchanges()
        print("Available exchanges:")
        for idx, exchange in enumerate(available_exchanges):
            print(f"{idx + 1}. {exchange}")

        selected_index = int(input("Select an exchange by number: ")) - 1
        if selected_index < 0 or selected_index >= len(available_exchanges):
            print('Invalid selection.')
            sys.exit(1)

        selected_exchange = available_exchanges[selected_index]
        run_update(selected_exchange)
