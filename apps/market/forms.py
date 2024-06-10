# forms.py
from datetime import datetime, timedelta
from django import forms
from .models import Backtest, Optimize, PaperTrade
from ..exchanges.models import Exchange, Market, Coin

class BacktestForm(forms.ModelForm):

    class Meta:
        model = Backtest
        fields = ['exchange', 'symbol', 'timeframe', 'cash', 'commission', 'start_date', 'end_date', 'openbrowser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].choices = [(exchange.id_char, exchange.name) for exchange in Exchange.objects.all()]
        print("Available exchanges:", self.fields['exchange'].choices)

        self.fields['symbol'].choices = []
        self.fields['timeframe'].choices = []

        if 'exchange' in self.data:
            try:
                exchange_id = self.data.get('exchange')
                print("Submitted exchange_id:", exchange_id)
                markets = Market.objects.filter(exchange__id_char=exchange_id)
                self.fields['symbol'].choices = [
                    (coin.symbol, coin.symbol) for coin in Coin.objects.filter(markets__exchange__id_char=exchange_id).distinct()
                ]
                self.fields['timeframe'].choices = [
                    (market.market_type, market.market_type) for market in markets
                ]
                print("Symbol choices based on exchange:", self.fields['symbol'].choices)
                print("Timeframe choices based on exchange:", self.fields['timeframe'].choices)
            except (ValueError, TypeError):
                print("Error processing exchange_id in form initialization")

        if 'market' in self.data:
            try:
                market_id = self.data.get('market')
                print("Submitted market_id:", market_id)
                coins = Coin.objects.filter(markets__id=market_id).distinct()
                self.fields['symbol'].choices = [(coin.symbol, coin.symbol) for coin in coins]
                self.fields['timeframe'].choices = [
                    ('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('1h', '1h'), ('4h', '4h'),
                    ('1d', '1d'), ('1w', '1w'), ('1M', '1M')
                ]
                print("Updated symbol choices based on market:", self.fields['symbol'].choices)
                print("Updated timeframe choices based on market:", self.fields['timeframe'].choices)
            except (ValueError, TypeError):
                print("Error processing market_id in form initialization")

        # Set initial values for date fields if not already set
        if not self.fields['start_date'].initial:
            self.fields['start_date'].initial = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not self.fields['end_date'].initial:
            self.fields['end_date'].initial = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        print("Initial start_date:", self.fields['start_date'].initial)
        print("Initial end_date:", self.fields['end_date'].initial)

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
        self.fields['exchange'].choices = [(exchange.id_char, exchange.name) for exchange in Exchange.objects.all()]
        self.fields['symbol'].choices = []
        self.fields['timeframe'].choices = []

        if 'exchange' in self.data:
            try:
                exchange_id = self.data.get('exchange')
                self.fields['symbol'].choices = self.get_symbol_choices(exchange_id)
                self.fields['timeframe'].choices = self.get_timeframe_choices(exchange_id)
            except (ValueError, TypeError):
                pass

    def get_symbol_choices(self, exchange_id):
        coins = Coin.objects.filter(markets__exchange_id=exchange_id).distinct()
        return [(coin.symbol, coin.symbol) for coin in coins]

    def get_timeframe_choices(self, exchange_id):
        return [('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('1h', '1h'), ('4h', '4h'), ('1d', '1d'), ('1w', '1w'), ('1M', '1M')]


class CreatePaperTradeForm(forms.ModelForm):
    class Meta:
        model = PaperTrade
        fields = ['name', 'initial_balance', 'exchange', 'coin', 'type', 'timeframe', 'cron_timeframe',
                  'lookback_period', 'atr_timeperiod', 'atr_multiplier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].queryset = Exchange.objects.all()
        self.fields['coin'].choices = []
        self.fields['timeframe'].choices = []
        self.fields['type'].choices = []

        self.fields['name'].initial = "Default Trade Name"
        self.fields['initial_balance'].initial = 1000
        self.fields['cron_timeframe'].initial = 60
        self.fields['lookback_period'].initial = 7

        self.fields['name'].label = "Trade Name"
        self.fields['initial_balance'].label = "Initial Balance"
        self.fields['cron_timeframe'].label = "Cron Timeframe (in seconds)"
        self.fields['lookback_period'].label = "Lookback Period (in days)"
        self.fields['atr_timeperiod'].label = "ATR Timeperiod"
        self.fields['atr_multiplier'].label = "ATR Multiplier"

from django import forms
from .models import PaperTrade

from django import forms
from .models import PaperTrade

class TradeParametersForm(forms.ModelForm):
    class Meta:
        model = PaperTrade
        fields = ['take_profit', 'stop_loss', 'trading_fee', 'initial_account', 'x_prices']
        widgets = {
            'take_profit': forms.NumberInput(attrs={'step': '0.0001', 'min': '0'}),
            'stop_loss': forms.NumberInput(attrs={'step': '0.0001', 'min': '0'}),
            'trading_fee': forms.NumberInput(attrs={'step': '0.0001', 'min': '0'}),
            'initial_account': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'x_prices': forms.NumberInput(attrs={'step': '1', 'min': '1'})
        }

from django import forms

class OptimizationForm(forms.Form):
    take_profit_min = forms.DecimalField(label="Take Profit Min", max_digits=5, decimal_places=2)
    take_profit_max = forms.DecimalField(label="Take Profit Max", max_digits=5, decimal_places=2)
    take_profit_step = forms.DecimalField(label="Take Profit Step", max_digits=5, decimal_places=2)
    stop_loss_min = forms.DecimalField(label="Stop Loss Min", max_digits=5, decimal_places=2)
    stop_loss_max = forms.DecimalField(label="Stop Loss Max", max_digits=5, decimal_places=2)
    stop_loss_step = forms.DecimalField(label="Stop Loss Step", max_digits=5, decimal_places=2)
    x_prices_min = forms.IntegerField(label="X Prices Min")
    x_prices_max = forms.IntegerField(label="X Prices Max")
    x_prices_step = forms.IntegerField(label="X Prices Step")
