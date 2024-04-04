from django.shortcuts import render
from .models import Exchange
from django.shortcuts import redirect
from .forms import ExchangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

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