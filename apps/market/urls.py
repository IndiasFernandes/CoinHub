from django.urls import path
from .views import (
    CreatePaperTradeView, run_backtest_view, run_optimization_view,
    backtests_list_view, backtest_detail_view, optimize_list_view, optimize_detail_view,
    market_dashboard_view, load_markets, load_symbols_and_timeframes,
    TogglePaperTradingView, delete_paper_trade,
    paper_trading_dashboard_view, paper_trade_detail_view, fetch_market_data
)

app_name = 'market'

urlpatterns = [
    path('', market_dashboard_view, name='market_dashboard'),
    path('backtest/', run_backtest_view, name='run_backtest'),
    path('backtests/', backtests_list_view, name='backtests_list'),
    path('backtests/<int:backtest_id>/', backtest_detail_view, name='backtest_detail'),
    path('optimize/', run_optimization_view, name='run_optimization'),
    path('optimizations/', optimize_list_view, name='optimize_list'),
    path('optimize/<int:optimize_id>/', optimize_detail_view, name='optimize_detail'),
    path('paper-trading/', paper_trading_dashboard_view, name='paper_trading_dashboard'),
    path('paper-trades/<int:trade_id>/', paper_trade_detail_view, name='paper_trade_detail'),
    path('delete-paper-trade/<int:trade_id>/', delete_paper_trade, name='delete_paper_trade'),
    path('create-paper-trade/', CreatePaperTradeView.as_view(), name='create_paper_trade'),
    path('ajax/load-markets/', load_markets, name='ajax_load_markets'),
    path('ajax/load-symbols-timeframes/', load_symbols_and_timeframes, name='ajax_load_symbols_timeframes'),
    path('toggle-trade-active/<int:trade_id>/', TogglePaperTradingView.as_view(), name='toggle_trade_active'),
    path('fetch-market-data/<int:trade_id>/', fetch_market_data, name='fetch_market_data'),
]
