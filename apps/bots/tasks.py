# tasks.py in your bots app
import os
from _decimal import Decimal
from datetime import datetime

from django.utils import timezone

from CoinHub import settings
from ..exchanges.utils.ccxt_experience import run_hyperliquid
from ..exchanges.utils.hyperliquid.bot import BotAccount
from celery import shared_task
from .models import Bot
import time

from CoinHub.celery import app
from .models import BotEvaluation
from apps.market.models import Optimize
import requests  # Assuming you're using requests to fetch current market prices

from ..exchanges.utils.hyperliquid.download_data import download_data
from ..market.views import perform_backtest


@shared_task(bind=True)
def analyze_cryptos(self, bot_id, sleep_time):
    try:
        bot = Bot.objects.get(id=bot_id)
        print(f"Bot with ID {bot_id} found.")
    except Bot.DoesNotExist:
        print(f"Bot with ID {bot_id} does not exist.")
        return

    bot.task_id = self.request.id
    bot.save(update_fields=['task_id'])
    exchange = run_hyperliquid()
    bot_account = BotAccount()
    bot_account.test_functions()


    while bot.is_active:

        # Your bot's operational logic here
        print(f"Running bot loop for {bot.name}")

        # Refresh the bot instance from the database to get the latest status
        bot_account.update_exchange_info()
        bot_account.updated_at = timezone.now()

        print(f"Running bot loop for {bot.name}")


        optimized_cryptos = Optimize.objects.filter(return_percent__gt=400)
        print(f'Analyzing {optimized_cryptos.count()} optimized cryptos...')
        print(f"Optimized cryptos: {optimized_cryptos}")
        coin_list = exchange.fetch_markets()
        for crypto in optimized_cryptos:
            try:
                # get st and price
                print(crypto.start_date)
                start_timestamp = str(crypto.start_date)[:-15]
                end_timestamp = str(crypto.end_date)[:-15]
                atr_timeperiod = crypto.atr_timeperiod
                atr_multiplier = crypto.atr_multiplier

                with open(os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_atr_timeperiod.csv'), 'w') as f:
                    f.write(str(atr_multiplier))
                with open(os.path.join(settings.BASE_DIR, 'static', 'backtest', 'current_backtest_multiplier.csv'), 'w') as f:
                    f.write(str(atr_timeperiod))

                print(f"ATR Timeperiod: {atr_timeperiod}, ATR Multiplier: {atr_multiplier}")




                print(start_timestamp)
                print(end_timestamp)

                df = download_data([str(crypto.symbol)], [str(crypto.timeperiod)], start_timestamp, end_timestamp, exchange)
                backtest_result =perform_backtest(df, crypto.symbol, crypto.timeperiod)
                current_price = backtest_result['price']
                # use the last value of price from the database df as the last price


                #TODO: use the last value from the database df
                st_value = backtest_result['st']
                print(f"Current price: {current_price}, ST value: {st_value}")
                st_higher = st_value > current_price
                st_lower = st_value < current_price

                percentage_difference = abs((st_value - current_price) / current_price * 100)

                # BotEvaluation.objects.create(
                #     symbol=str(crypto.symbol)+'_'+str(crypto.timeperiod),
                #     st=st_value,
                #     optimize=crypto,
                #     current_price=float(current_price),
                #     st_higher=st_higher,
                #     st_lower=st_lower,
                #     percentage_difference=percentage_difference
                # )
            except Exception as e:
                print(f"Error analyzing crypto {crypto.symbol}: {e}")
        time.sleep(sleep_time)

    bot.is_active = False  # This should be controlled by your actual bot's status check logic.
    bot.task_id = ''
    bot.save(update_fields=['task_id'])

def get_price(coin_list, symbol):
    # Search for the coin by its symbol
    print(f"Coin list: {coin_list}")
    for coin in coin_list:
        print(coin.get('info', {}).get('price'))
        if coin['symbol'] == symbol:
            # Check if price information is available

            if 'price' in coin.get('info', {}):
                return coin['info']['price']
            else:
                return f"Price information not available for {symbol}."
    return f"Coin symbol {symbol} not found."

@shared_task
def update_bot_status_and_values(bot_id):
    bot = Bot.objects.get(id=bot_id)
    if bot.is_active:
        bot.is_active = not bot.is_active
        bot = BotAccount()
        bot.update_exchange_info()
        bot.updated_at = timezone.now()
        print(f"Bot updated at {bot.updated_at}")
        time.sleep(5)

@shared_task(bind=True)
def run_bot_loop(self, bot_id, sleep_time):
    try:
        bot = Bot.objects.get(id=bot_id)
    except Bot.DoesNotExist:
        return

    # Store the current task id in the bot instance
    bot.task_id = self.request.id
    bot.save(update_fields=['task_id'])
    bot_account = BotAccount()
    bot_account.test_functions()
    while bot.is_active:

        # Your bot's operational logic here
        print(f"Running bot loop for {bot.name}")
        time.sleep(sleep_time)  # Adjust the sleep time as needed

        # Refresh the bot instance from the database to get the latest status
        bot_account.update_exchange_info()
        bot_account.updated_at = timezone.now()

    # Clear the task_id once the loop is done
    bot.task_id = ''
    bot.save(update_fields=['task_id'])