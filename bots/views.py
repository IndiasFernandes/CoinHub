
from django.shortcuts import render, get_object_or_404
from .models import Bot

def bot_list(request):
    # Dummy data
    bots = [
        {'id': 1, 'name': 'Bot A', 'description': 'Description A', 'status': 'Active', 'strategy': 'Strategy A'},
        {'id': 2, 'name': 'Bot B', 'description': 'Description B', 'status': 'Inactive', 'strategy': 'Strategy B'},
        # Add more dummy bots as needed
    ]
    return render(request, 'pages/bots/bot_list.html', {'bots': bots})


def bot_detail(request, bot_id):

    bot = get_object_or_404(Bot, pk=bot_id)
    return render(request, 'pages/bots/bot_detail.html', {'bot': bot})


def bot_new(request):
    return render(request, 'pages/bots/bot_new.html')