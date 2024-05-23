# admin.py

from django.contrib import admin
from .models import Backtest, Optimize

class BacktestAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date')
    list_filter = ('symbol', 'timeframe', 'start_date', 'end_date')

class OptimizeAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'timeframe', 'cash', 'commission', 'sharpe_ratio', 'return_percent', 'created_at')
    list_filter = ('symbol', 'timeframe', 'start_date', 'end_date')

admin.site.register(Backtest, BacktestAdmin)
admin.site.register(Optimize, OptimizeAdmin)
