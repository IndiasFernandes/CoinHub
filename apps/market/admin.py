from django.contrib import admin
from .models import Optimize, Backtest

# Admin model for Optimize
class OptimizeAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'timeperiod', 'sharpe_ratio', 'return_percent', 'max_drawdown_percent', 'created_at')
    list_filter = ('symbol', 'timeperiod')
    search_fields = ('symbol', 'timeperiod')

# Admin model for Backtest
class BacktestAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'timeperiod', 'sharpe_ratio', 'return_percent', 'max_drawdown_percent', 'created_at')
    list_filter = ('symbol', 'timeperiod')
    search_fields = ('symbol', 'timeperiod')

# Register your models here
admin.site.register(Optimize, OptimizeAdmin)
admin.site.register(Backtest, BacktestAdmin)
