from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bot, Trade, Strategy
from .forms import BotForm, StrategyForm
from CoinHub.celery import app  # Assuming 'app' is correctly configured in your Celery instance


@login_required
def bot_list(request):
    bots = Bot.objects.filter(user=request.user)
    return render(request, 'pages/bots/bot_list.html', {
        'bots': bots,
        'current_section': 'bots'
    })

@login_required
def bot_detail(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)
    trades = Trade.objects.filter(bot=bot).order_by('-timestamp')
    return render(request, 'pages/bots/bot_detail.html', {
        'bot': bot,
        'trades': trades,
        'current_section': 'bots'
    })

@login_required
def bot_new(request):
    if request.method == 'POST':
        form = BotForm(request.POST)
        if form.is_valid():
            bot = form.save(commit=False)
            bot.user = request.user
            bot.save()
            messages.success(request, f'Bot {bot.name} created successfully!')
            return redirect('bot:bot_detail', bot_id=bot.pk)
    else:
        form = BotForm()
    return render(request, 'pages/bots/bot_new.html', {
        'form': form,
        'current_section': 'bots'
    })

@login_required
def delete_bot(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)
    if request.method == 'POST':
        bot_name = bot.name
        bot.delete()
        messages.success(request, f'Bot {bot_name} deleted successfully!')
        return redirect('bot:bot_list')
    return redirect('bot:bot_detail', bot_id=bot_id)

@login_required
def toggle_bot_status(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)
    bot.is_active = not bot.is_active
    bot.save()
    if bot.is_active:
        messages.success(request, f'Bot {bot.name} has been activated!')
        # Start or restart the bot loop task

        task = app.send_task('apps.bots.tasks.analyze_cryptos', args=[bot_id, 60])
        # analyze_cryptos.delay()  # Schedule the task when the bot is activated
        bot.task_id = task.id
        bot.save(update_fields=['task_id'])
    else:
        messages.success(request, f'Bot {bot.name} has been deactivated!')
        if bot.task_id:
            app.control.revoke(bot.task_id, terminate=True)
            bot.task_id = ''
            bot.save(update_fields=['task_id'])
    return redirect('bot:bot_list')

class CurrentSectionMixin:
    current_section = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.current_section:
            context['current_section'] = self.current_section
        return context

class StrategyListView(LoginRequiredMixin, CurrentSectionMixin, ListView):
    model = Strategy
    template_name = 'pages/bots/strategy_list.html'
    current_section = 'bots'

class StrategyCreateView(LoginRequiredMixin, CurrentSectionMixin, CreateView):
    model = Strategy
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'

class StrategyEditView(LoginRequiredMixin, CurrentSectionMixin, UpdateView):
    model = Strategy
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'

class StrategyDeleteView(LoginRequiredMixin, CurrentSectionMixin, DeleteView):
    model = Strategy
    template_name = 'pages/bots/strategy_confirm_delete.html'
    success_url = reverse_lazy('bots:strategy_list')
    current_section = 'bots'


from django.shortcuts import render
from .models import BotEvaluation
from django.db.models import F


@login_required
def bot_evaluation_chart_view(request):
    # Fetch bot evaluations
    evaluations = BotEvaluation.objects.all().order_by('evaluated_at')

    # Prepare data for the chart
    data = {}
    for eval in evaluations:
        if eval.symbol not in data:
            data[eval.symbol] = {'timestamps': [], 'prices': [], 'st_values': []}
        data[eval.symbol]['timestamps'].append(eval.evaluated_at.strftime("%Y-%m-%d %H:%M:%S"))
        data[eval.symbol]['prices'].append(eval.current_price)
        data[eval.symbol]['st_values'].append(eval.st)

    context = {
        'data': data,
        'current_section': 'bot_evaluation',
        'current_section': 'bots'
    }
    return render(request, 'pages/bots/bot_evaluation_chart.html', context)
