# forms.py
from django import forms
from django.forms import ModelForm
from .models import Backtest, Optimize

class BacktestForm(ModelForm):
    cash = forms.DecimalField(label='Cash', max_digits=20, decimal_places=2)
    commission = forms.DecimalField(label='Commission', max_digits=5, decimal_places=4)
    openbrowser = forms.BooleanField(label='Open Browser', required=False)

    class Meta:
        model = Backtest
        fields = ['exchange_id', 'symbol', 'timeframe', 'start_date', 'end_date', 'cash', 'commission', 'openbrowser']

class OptimizeForm(ModelForm):
    cash = forms.DecimalField(label='Cash', max_digits=20, decimal_places=2)
    commission = forms.DecimalField(label='Commission', max_digits=5, decimal_places=4)
    openbrowser = forms.BooleanField(label='Open Browser', required=False)
    max_tries = forms.IntegerField(label='Max Tries')
    min_timeperiod = forms.DecimalField(label='Min Timeperiod', max_digits=10, decimal_places=2)
    max_timeperiod = forms.DecimalField(label='Max Timeperiod', max_digits=10, decimal_places=2)
    interval_timeperiod = forms.DecimalField(label='Interval Timeperiod', max_digits=10, decimal_places=2)
    min_multiplier = forms.DecimalField(label='Min Multiplier', max_digits=10, decimal_places=2)
    max_multiplier = forms.DecimalField(label='Max Multiplier', max_digits=10, decimal_places=2)
    interval_multiplier = forms.DecimalField(label='Interval Multiplier', max_digits=10, decimal_places=2)

    class Meta:
        model = Optimize
        fields = ['exchange_id', 'symbol', 'timeframe', 'start_date', 'end_date', 'cash', 'commission', 'openbrowser', 'max_tries', 'min_timeperiod', 'max_timeperiod', 'interval_timeperiod', 'min_multiplier', 'max_multiplier', 'interval_multiplier']
