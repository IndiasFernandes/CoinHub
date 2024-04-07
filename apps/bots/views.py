from django.contrib import messages
from .forms import BotForm
from django.shortcuts import render
from .models import Trade
from django.contrib.auth.decorators import login_required  # If you're using user authentication
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Bot
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Strategy
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import StrategyForm  # Import your custom form class


@login_required
def bot_list(request):
    # Fetch bots that belong to the current user
    bots = Bot.objects.filter(user=request.user)
    return render(request, 'pages/bots/bot_list.html', {'bots': bots})

@login_required
def bot_detail(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)  # Ensure the bot belongs to the logged-in user
    trades = Trade.objects.filter(bot=bot).order_by('-timestamp')  # Fetch trades related to the bot, newest first

    return render(request, 'pages/bots/bot_detail.html', {'bot': bot, 'trades': trades})

@login_required
def bot_new(request):
    if request.method == 'POST':
        form = BotForm(request.POST)
        if form.is_valid():
            bot = form.save(commit=False)
            bot.user = request.user  # Set the bot's user to the current user
            bot.save()
            messages.success(request, f'Bot {bot.name}  created successfully!')  # Success message
            return redirect('bot:bot_detail', bot_id=bot.pk)
    else:
        form = BotForm()
    return render(request, 'pages/bots/bot_new.html', {'form': form})


@login_required
def delete_bot(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id)
    if request.method == 'POST':
        bot_name = bot.name
        bot.delete()
        bots = Bot.objects.filter(user=request.user)
        messages.success(request, f'Bot {bot_name} successfully!')
        return render(request, 'pages/bots/bot_list.html', {'bots': bots})
    else:
        # If not a POST request, redirect to bot detail page or show a confirmation page
        return redirect(reverse('bot:bot_detail', kwargs={'bot_id': bot_id}))

@require_POST
def toggle_bot_status(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id)
    bot.is_active = not bot.is_active  # Toggle the is_active status
    if bot.is_active:
        messages.success(request, f'Bot {bot.name} has been activated!')
    else:
        messages.success(request, f'Bot {bot.name} has been deactivated!')
    bot.save()

    return HttpResponseRedirect(reverse('bots:bot_list'))  # Adjust 'bots:bot_list' to your actual bot listing URL name

class StrategyListView(ListView):
    model = Strategy
    template_name = 'pages/bots/strategy_list.html'


class StrategyCreateView(CreateView):
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    # Don't include 'fields' here

class StrategyEditView(UpdateView):
    model = Strategy
    fields = ['name', 'strategy_type', 'position', 'code']
    template_name = 'pages/bots/strategy_form.html'
    form_class = BotForm
    success_url = reverse_lazy('bots:strategy_list')  # Redirect to the strategy list after editing

class StrategyDeleteView(DeleteView):
    model = Strategy
    template_name = 'pages/bots/strategy_confirm_delete.html'
    success_url = reverse_lazy('bots:strategy_list')  # Redirect to the strategy list after deletion
    # template_name = 'bots/strategy_confirm_delete.html'  # If you have a confirmation template