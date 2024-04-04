from django.shortcuts import redirect
from .forms import BotForm
from django.shortcuts import render, get_object_or_404
from .models import Bot, Trade
from django.contrib.auth.decorators import login_required

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
            return redirect('bot:bot_detail', bot_id=bot.pk)
    else:
        form = BotForm()
    return render(request, 'pages/bots/bot_new.html', {'form': form})