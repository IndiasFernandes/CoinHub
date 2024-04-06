from django.shortcuts import render
from .models import Exchange
from django.shortcuts import redirect
from .forms import ExchangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import ExchangeInfo

@login_required
def exchange_list(request):
    exchanges = Exchange.objects.all()
    return render(request, 'pages/exchanges/exchange_list.html', {'exchanges': exchanges})

@login_required
def exchange_detail(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id)
    return render(request, 'pages/exchanges/exchange_detail.html', {'exchange': exchange})

@login_required
def exchange_new(request):
    if request.method == 'POST':
        form = ExchangeForm(request.POST)
        if form.is_valid():
            exchange = form.save()
            return redirect('exchange:exchange_detail', exchange_id=exchange.pk)
    else:
        form = ExchangeForm()
    return render(request, 'pages/exchanges/exchange_new.html', {'form': form})




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
    }
    return render(request, 'pages/general/graphs/chart.html', context)