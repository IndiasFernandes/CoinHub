from .forms import BotForm
from django.shortcuts import render
from .models import Trade
from .models import Strategy
from .forms import StrategyForm  # Import your custom form class
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from CoinHub.celery import app  # Import the Celery app instance
from .models import Bot

@login_required
def bot_list(request):
    bots = Bot.objects.filter(user=request.user)
    return render(request, 'pages/bots/bot_list.html', {
        'bots': bots,
        'current_section': 'bots'  # Pass the current section
    })
@login_required
def bot_detail(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)  # Ensure the bot belongs to the logged-in user
    trades = Trade.objects.filter(bot=bot).order_by('-timestamp')  # Fetch trades related to the bot, newest first

    return render(request, 'pages/bots/bot_detail.html', {'bot': bot, 'trades': trades, 'current_section': 'bots'})

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
    return render(request, 'pages/bots/bot_new.html', {'form': form, 'current_section': 'bots'})


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
        return redirect(reverse('bot:bot_detail', kwargs={'bot_id': bot_id, 'current_section': 'bots'}))


@login_required
def toggle_bot_status(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)
    bot.is_active = not bot.is_active
    bot.save()

    if bot.is_active:
        messages.success(request, f'Bot {bot.name} has been activated!')
        # Start the bot loop task
        task = app.send_task('apps.bots.tasks.run_bot_loop', args=[bot.id, 30])
    else:
        messages.success(request, f'Bot {bot.name} has been deactivated!')
        # Stop the bot loop task if it's running
        if bot.task_id:
            app.control.revoke(bot.task_id, terminate=True)
            bot.task_id = ''
            bot.save(update_fields=['task_id'])

    return redirect('bots:bot_list')
class CurrentSectionMixin:
    current_section = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.current_section:
            context['current_section'] = self.current_section
        return context

class StrategyListView(CurrentSectionMixin, ListView):
    model = Strategy
    template_name = 'pages/bots/strategy_list.html'
    current_section = 'bots'

class StrategyCreateView(CurrentSectionMixin, CreateView):
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'

class StrategyEditView(CurrentSectionMixin, UpdateView):
    model = Strategy
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'

class StrategyDeleteView(CurrentSectionMixin, DeleteView):
    model = Strategy
    template_name = 'pages/bots/strategy_confirm_delete.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'
