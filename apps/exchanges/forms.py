from datetime import datetime, timedelta
from django import forms
from .models import Exchange, Market, Coin


# forms.py

from datetime import datetime, timedelta
from django import forms
from .models import Exchange, Market, Coin

class DownloadDataForm(forms.Form):
    exchange_id = forms.ChoiceField(choices=[], label="Exchange")
    market = forms.ChoiceField(choices=[], label="Market")
    symbol = forms.MultipleChoiceField(choices=[], label="Symbol")
    timeframe = forms.MultipleChoiceField(choices=[], label="Timeframe")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange_id'].choices = [(exchange.id_char, exchange.name) for exchange in Exchange.objects.all()]
        self.fields['market'].choices = []

        if 'exchange_id' in self.data:
            try:
                exchange_id = self.data.get('exchange_id')
                markets = Market.objects.filter(exchange__id_char=exchange_id)
                self.fields['market'].choices = [(market.id, market.market_type) for market in markets]
            except (ValueError, TypeError):
                pass

        if 'market' in self.data:
            try:
                market_id = int(self.data.get('market'))
                coins = Coin.objects.filter(markets__id=market_id).distinct()
                self.fields['symbol'].choices = [(coin.symbol, coin.symbol) for coin in coins]
                self.fields['timeframe'].choices = [
                    ('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('1h', '1h'), ('4h', '4h'),
                    ('1d', '1d'), ('1w', '1w'), ('1M', '1M')
                ]
            except (ValueError, TypeError):
                pass

        # Set initial values for date fields if not already set
        if not self.fields['start_date'].initial:
            self.fields['start_date'].initial = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not self.fields['end_date'].initial:
            self.fields['end_date'].initial = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = ['name', 'description', 'api_url', 'api_key', 'secret_key', 'id_char']


class MarketForm(forms.ModelForm):
    exchange = forms.ModelChoiceField(queryset=Exchange.objects.all(), to_field_name='id_char', required=True)

    class Meta:
        model = Market
        fields = ['market_type', 'coins', 'exchange']
        widgets = {
            'coins': forms.CheckboxSelectMultiple,
        }
