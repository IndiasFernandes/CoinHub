from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bot, Trade, Strategy, BotEvaluation
from .forms import BotForm, StrategyForm
from CoinHub.celery import app

@login_required
def bots_dashboard_view(request):
    return render(request, 'pages/bots/dashboard.html', {
        'current_section': 'bots',
        'section': 'dashboard',
        'show_sidebar': True
    })

class CurrentSectionMixin:
    current_section = 'bots'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_section'] = self.current_section
        context['show_sidebar'] = True
        return context

@login_required
def bot_list(request):
    bots = Bot.objects.filter(user=request.user)
    context = {
        'bots': bots,
        'section': 'bot_list',
        'current_section': 'bots',
        'show_sidebar': True
    }
    return render(request, 'pages/bots/bot_list.html', context)

@login_required
def bot_detail(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id, user=request.user)
    trades = Trade.objects.filter(bot=bot).order_by('-timestamp')
    context = {
        'bot': bot,
        'trades': trades,
        'section': 'bot_detail',
        'current_section': 'bots',
        'show_sidebar': True
    }
    return render(request, 'pages/bots/bot_detail.html', context)

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
    context = {
        'form': form,
        'current_section': 'bots',
        'section': 'bot_new',
        'show_sidebar': True
    }
    return render(request, 'pages/bots/bot_new.html', context)

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
        task = app.send_task('apps.bots.tasks.analyze_cryptos', args=[bot_id, 60])
        bot.task_id = task.id
        bot.save(update_fields=['task_id'])
    else:
        messages.success(request, f'Bot {bot.name} has been deactivated!')
        if bot.task_id:
            app.control.revoke(bot.task_id, terminate=True)
            bot.task_id = ''
            bot.save(update_fields=['task_id'])
    return redirect('bot:bot_list')

class StrategyListView(LoginRequiredMixin, CurrentSectionMixin, ListView):
    model = Strategy
    template_name = 'pages/bots/strategy_list.html'
    context_object_name = 'strategies'
    section = 'strategy_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context

class StrategyCreateView(LoginRequiredMixin, CurrentSectionMixin, CreateView):
    model = Strategy
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    section = 'strategy_new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context

class StrategyEditView(LoginRequiredMixin, CurrentSectionMixin, UpdateView):
    model = Strategy
    form_class = StrategyForm
    template_name = 'pages/bots/strategy_form.html'
    success_url = reverse_lazy('bots:strategy_list')
    section = 'strategy_edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context

class StrategyDeleteView(LoginRequiredMixin, CurrentSectionMixin, DeleteView):
    model = Strategy
    template_name = 'pages/bots/strategy_confirm_delete.html'
    success_url = reverse_lazy('bots:strategy_list')
    section = 'strategy_delete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context

@login_required
def bot_evaluation_chart_view(request):
    evaluations = BotEvaluation.objects.all().order_by('evaluated_at')
    data = {}
    for eval in evaluations:
        if eval.symbol not in data:
            data[eval.symbol] = {'timestamps': [], 'prices': [], 'st_values': []}
        data[eval.symbol]['timestamps'].append(eval.evaluated_at.strftime("%Y-%m-%d %H:%M:%S"))
        data[eval.symbol]['prices'].append(eval.current_price)
        data[eval.symbol]['st_values'].append(eval.st)
    context = {
        'data': data,
        'current_section': 'bots',
        'section': 'bot_evaluation_chart',
        'show_sidebar': True
    }
    return render(request, 'pages/bots/bot_evaluation_chart.html', context)
