# forms.py
from django import forms
from .models import Backtest, Optimize


class BacktestForm(forms.ModelForm):
    class Meta:
        model = Backtest
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date', 'openbrowser']


class OptimizeForm(forms.ModelForm):
    min_timeperiod = forms.FloatField()
    max_timeperiod = forms.FloatField()
    interval_timeperiod = forms.FloatField()
    min_multiplier = forms.FloatField()
    max_multiplier = forms.FloatField()
    interval_multiplier = forms.FloatField()

    class Meta:
        model = Optimize
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date',
                  'max_tries', 'openbrowser', 'min_timeperiod', 'max_timeperiod',
                  'interval_timeperiod', 'min_multiplier', 'max_multiplier', 'interval_multiplier']
