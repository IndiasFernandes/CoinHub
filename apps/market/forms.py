from django import forms
from .models import Backtest, Optimize
from ..exchanges.models import Exchange, Market, Coin

class BacktestForm(forms.ModelForm):
    class Meta:
        model = Backtest
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date', 'openbrowser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].queryset = Exchange.objects.all()
        self.fields['symbol'].choices = []
        self.fields['timeframe'].choices = []

        if 'exchange' in self.data:
            try:
                exchange_id = self.data.get('exchange')
                markets = Market.objects.filter(exchange_id=exchange_id)
                symbols = Coin.objects.filter(markets__in=markets).distinct()
                self.fields['symbol'].choices = [(symbol.id, symbol.symbol) for symbol in symbols]
                self.fields['timeframe'].choices = [(market.market_type, market.market_type) for market in markets]
            except (ValueError, TypeError):
                pass

class OptimizeForm(forms.ModelForm):
    min_timeperiod = forms.FloatField()
    max_timeperiod = forms.FloatField()
    interval_timeperiod = forms.FloatField()
    min_multiplier = forms.FloatField()
    max_multiplier = forms.FloatField()
    interval_multiplier = forms.FloatField()

    class Meta:
        model = Optimize
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date', 'max_tries', 'openbrowser', 'min_timeperiod', 'max_timeperiod', 'interval_timeperiod', 'min_multiplier', 'max_multiplier', 'interval_multiplier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].queryset = Exchange.objects.all()
        self.fields['symbol'].choices = []
        self.fields['timeframe'].choices = []

        if 'exchange' in self.data:
            try:
                exchange_id = self.data.get('exchange')
                markets = Market.objects.filter(exchange_id=exchange_id)
                symbols = Coin.objects.filter(markets__in=markets).distinct()
                self.fields['symbol'].choices = [(symbol.id, symbol.symbol) for symbol in symbols]
                self.fields['timeframe'].choices = [(market.market_type, market.market_type) for market in markets]
            except (ValueError, TypeError):
                pass
