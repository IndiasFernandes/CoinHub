from django.urls import path
from . import views

app_name = 'bot'

urlpatterns = [
    path('list/', views.bot_list, name='bot_list'),
    path('bots/<int:bot_id>/', views.bot_detail, name='bot_detail'),
    path('new/', views.bot_new, name='bot_new'),
]
