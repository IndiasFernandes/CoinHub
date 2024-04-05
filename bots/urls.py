from django.urls import path
from . import views

app_name = 'bot'

urlpatterns = [
    path('', views.bot_list, name='bot_list'),
    path('<int:bot_id>/', views.bot_detail, name='bot_detail'),
    path('new/', views.bot_new, name='bot_new'),
    path('delete/<int:bot_id>/', views.delete_bot, name='delete_bot'),
]
