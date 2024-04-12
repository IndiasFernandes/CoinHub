# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('backtest/', views.run_backtest, name='run_backtest'),
    path('backtests/', views.backtest_list, name='backtests_list'),
    path('backtests/<int:backtest_id>/', views.backtest_detail, name='backtest_detail'),
    path('optimize/', views.run_optimization, name='run_optimization'),
    path('optimizations/', views.optimize_list, name='optimize_list'),
    path('optimize/<int:optimize_id>/', views.optimize_detail, name='optimize_detail'),
]