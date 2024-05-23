from django.urls import path
from .views import StrategyListView, StrategyCreateView, bot_evaluation_chart_view
from . import views

app_name = 'bot'

urlpatterns = [
    path('', views.bot_list, name='bot_list'),
    path('<int:bot_id>/', views.bot_detail, name='bot_detail'),
    path('new/', views.bot_new, name='bot_new'),
    path('delete/<int:bot_id>/', views.delete_bot, name='delete_bot'),
    path('toggle-status/<int:bot_id>/', views.toggle_bot_status, name='toggle_bot_status'),
    path('strategies/', StrategyListView.as_view(), name='strategy_list'),
    path('strategies/new/', StrategyCreateView.as_view(), name='strategy_create'),
    path('strategies/edit/<int:pk>/', views.StrategyEditView.as_view(), name='strategy_edit'),
    path('strategies/delete/<int:pk>/', views.StrategyDeleteView.as_view(), name='strategy_delete'),
    path('bot-evaluation-chart/', bot_evaluation_chart_view, name='bot_evaluation_chart'),
]
