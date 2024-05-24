# forms.py

from django import forms
from .models import Backtest, Optimize
from ..exchanges.exchange_data import EXCHANGES

class BacktestForm(forms.ModelForm):
    class Meta:
        model = Backtest
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date', 'openbrowser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'exchange' in self.data:
            exchange_id = self.data.get('exchange')
            exchange_data = EXCHANGES.get(exchange_id)
            if exchange_data:
                self.fields['symbol'].choices = [(symbol, symbol) for symbol in exchange_data['symbols']]
                self.fields['timeframe'].choices = [(timeframe, timeframe) for timeframe in exchange_data['timeframes']]
        else:
            # Set default choices
            default_exchange = list(EXCHANGES.keys())[0]
            self.fields['symbol'].choices = [(symbol, symbol) for symbol in EXCHANGES[default_exchange]['symbols']]
            self.fields['timeframe'].choices = [(timeframe, timeframe) for timeframe in EXCHANGES[default_exchange]['timeframes']]

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'exchange' in self.data:
            exchange_id = self.data.get('exchange')
            exchange_data = EXCHANGES.get(exchange_id)
            if exchange_data:
                self.fields['symbol'].choices = [(symbol, symbol) for symbol in exchange_data['symbols']]
                self.fields['timeframe'].choices = [(timeframe, timeframe) for timeframe in exchange_data['timeframes']]
        else:
            # Set default choices
            default_exchange = list(EXCHANGES.keys())[0]
            self.fields['symbol'].choices = [(symbol, symbol) for symbol in EXCHANGES[default_exchange]['symbols']]
            self.fields['timeframe'].choices = [(timeframe, timeframe) for timeframe in EXCHANGES[default_exchange]['timeframes']]
