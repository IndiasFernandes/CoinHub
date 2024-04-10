from django.contrib import messages
from django.shortcuts import render
from .models import Exchange
from django.shortcuts import redirect
from .forms import ExchangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import ExchangeInfo
import requests
from .models import Exchange, Market, Coin
from .utils.hyperliquid.utils import BotAccount, print_main


@login_required
def exchange_list(request):
    exchanges = Exchange.objects.all()
    return render(request, 'pages/exchanges/exchange_list.html', {'exchanges': exchanges, 'current_section': 'exchanges'})

@login_required
def exchange_detail(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id)
    return render(request, 'pages/exchanges/exchange_detail.html', {'exchange': exchange, 'current_section': 'exchanges'})

@login_required
def exchange_new(request):
    if request.method == 'POST':
        form = ExchangeForm(request.POST)
        if form.is_valid():
            exchange = form.save()
            return redirect('exchange:exchange_detail', exchange_id=exchange.pk)
    else:
        form = ExchangeForm()
    return render(request, 'pages/exchanges/exchange_new.html', {'form': form, 'current_section': 'exchanges'})




@login_required
def chart_view(request):

    exchange_infos = ExchangeInfo.objects.all().order_by('timestamp')
    timestamps = [info.timestamp.strftime("%Y-%m-%d %H:%M:%S") for info in exchange_infos]
    account_values = [float(info.account_value) for info in exchange_infos]  # Convert to float
    withdrawable_values = [float(info.withdrawable) for info in exchange_infos]  # New line

    context = {
        'timestamps': timestamps,
        'account_values': account_values,
        'withdrawable_values': withdrawable_values,  # New line
        'current_section': 'exchanges'
    }
    return render(request, 'pages/general/graphs/chart.html', context)


@login_required
def update_market_coins(request, market_id):
    market = get_object_or_404(Market, pk=market_id)

    try:

        bot_account = BotAccount()
        # print a break in the command line that is visible and with a proper line
        print("\n")
        coins_prices = bot_account.all_coins()
        print("\n")
        for coin_symbol in coins_prices:
            coin, created = Coin.objects.get_or_create(symbol=coin_symbol)
            market.coins.add(coin)

        market.save()
        messages.success(request, "Market coins updated successfully.")

    except requests.RequestException as e:
        messages.error(request, f"Failed to update market coins: {e}")

    return redirect('exchange:exchange_detail', exchange_id=market.exchange.pk)