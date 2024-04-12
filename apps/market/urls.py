# urls.py

from django.urls import path
from . import views
from .views import run_backtest

urlpatterns = [
    path('backtest/', run_backtest, name='run_backtest'),
    path('backtests/', views.backtest_list, name='backtests_list'),
    path('backtests/<int:backtest_id>/', views.backtest_detail, name='backtest_detail'),
]