from datetime import datetime, timedelta
from django import forms
from .models import Exchange, Market, Coin


class DownloadDataForm(forms.Form):
    exchange_id = forms.ChoiceField(choices=[], label="Exchange")
    market = forms.ChoiceField(choices=[], label="Market")
    symbol = forms.MultipleChoiceField(choices=[], label="Symbol")
    timeframe = forms.MultipleChoiceField(choices=[], label="Timeframe")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                                 initial=datetime.now().replace(day=1).strftime('%Y-%m-%d'))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                               initial=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange_id'].choices = [(exchange.id_char, exchange.name) for exchange in Exchange.objects.all()]
        self.fields['market'].choices = []

        if 'exchange_id' in self.data:
            try:
                exchange_id = self.data.get('exchange_id')
                markets = Market.objects.filter(exchange_id=exchange_id)
                self.fields['market'].choices = [(market.id, market.market_type) for market in markets]
            except (ValueError, TypeError):
                pass

        if 'market' in self.data:
            try:
                market_id = int(self.data.get('market'))
                coins = Coin.objects.filter(markets__id=market_id).distinct()
                timeframes = Market.objects.filter(id=market_id).values_list('market_type', flat=True).distinct()
                self.fields['symbol'].choices = [(coin.symbol, coin.symbol) for coin in coins]
                self.fields['timeframe'].choices = [(timeframe, timeframe) for timeframe in timeframes]
            except (ValueError, TypeError):
                pass

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
