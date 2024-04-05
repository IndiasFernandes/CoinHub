from .forms import BotForm
from django.shortcuts import render, get_object_or_404
from .models import Trade
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Bot  # Assuming your model is named Bot
from django.contrib.auth.decorators import login_required  # If you're using user authentication

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



@login_required
def delete_bot(request, bot_id):
    bot = get_object_or_404(Bot, pk=bot_id)
    if request.method == 'POST':
        bot.delete()
        bots = Bot.objects.filter(user=request.user)
        return render(request, 'pages/bots/bot_list.html', {'bots': bots})
    else:
        # If not a POST request, redirect to bot detail page or show a confirmation page
        return redirect(reverse('bot:bot_detail', kwargs={'bot_id': bot_id}))