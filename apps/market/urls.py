from django.urls import path
from .views import PaperTradingDashboardView, CreatePaperTradeView, run_backtest_view, run_optimization_view, \
    backtests_list_view, backtest_detail_view, optimize_list_view, optimize_detail_view, market_dashboard_view, \
    load_markets, load_symbols_and_timeframes, TogglePaperTradingView

app_name = 'market'

urlpatterns = [
    path('', market_dashboard_view, name='market_dashboard'),
    path('backtest/', run_backtest_view, name='run_backtest'),
    path('backtests/', backtests_list_view, name='backtests_list'),
    path('backtests/<int:backtest_id>/', backtest_detail_view, name='backtest_detail'),
    path('optimize/', run_optimization_view, name='run_optimization'),
    path('optimizations/', optimize_list_view, name='optimize_list'),
    path('optimize/<int:optimize_id>/', optimize_detail_view, name='optimize_detail'),
    path('paper-trading/', PaperTradingDashboardView.as_view(), name='paper_trading_dashboard'),
    path('create-paper-trade/', CreatePaperTradeView.as_view(), name='create_paper_trade'),
    path('ajax/load-markets/', load_markets, name='ajax_load_markets'),
    path('ajax/load-symbols-timeframes/', load_symbols_and_timeframes, name='ajax_load_symbols_timeframes'),
    path('toggle-trade-active/<int:trade_id>/', TogglePaperTradingView.as_view(), name='toggle_trade_active'),  # Ensure this matches your actual view name
]
