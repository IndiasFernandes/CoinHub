# exchanges/models.py
from django.db import models


class Exchange(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    api_url = models.URLField()
    def __str__(self):
        return self.name

class Coin(models.Model):
    symbol = models.CharField(max_length=10)  # Example: BTC, ETH
    def __str__(self):
        return self.symbol

class Market(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    market_type = models.CharField(max_length=20, default='spot')  # Add a field for market type
    coins = models.ManyToManyField(Coin, related_name='markets')
    def __str__(self):
        return f"{self.exchange.name} - {self.market_type}"

class HistoricalData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    open_price = models.DecimalField(max_digits=15, decimal_places=5)
    close_price = models.DecimalField(max_digits=15, decimal_places=5)
    high_price = models.DecimalField(max_digits=15, decimal_places=5)
    low_price = models.DecimalField(max_digits=15, decimal_places=5)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    timestamp = models.DateTimeField()

    def __str__(self):
        # Assuming you want to list all related coins' symbols:
        coins_symbols = ", ".join([coin.symbol for coin in self.market.coins.all()])
        return f'Market: {self.market.exchange.name} - {self.market.market_type}, Coins: {coins_symbols}, Timestamp: {self.timestamp}'

    class Meta:
        verbose_name = "Historical Data"
        verbose_name_plural = "Historical Data"

class ExchangeInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_margin_used = models.DecimalField(max_digits=10, decimal_places=2)
    total_net_position = models.DecimalField(max_digits=10, decimal_places=2)
    total_raw_usd = models.DecimalField(max_digits=10, decimal_places=2)
    withdrawable = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Exchange Information"

# forms.py

from django import forms
from datetime import datetime, timedelta


class DownloadDataForm(forms.Form):
    EXCHANGE_CHOICES = [
        ('hyperliquid', 'HyperLiquid'),
        # Add more exchanges as needed
    ]
    SYMBOL_CHOICES = [
        ('AAVE/USDC:USDC', 'AAVE-USDC'),
        ('ACE/USDC:USDC', 'ACE-USDC'),
        ('ADA/USDC:USDC', 'ADA-USDC'),
        ('AI/USDC:USDC', 'AI-USDC'),
        ('ALT/USDC:USDC', 'ALT-USDC'),
        ('APE/USDC:USDC', 'APE-USDC'),
        ('APT/USDC:USDC', 'APT-USDC'),
        ('AR/USDC:USDC', 'AR-USDC'),
        ('ARB/USDC:USDC', 'ARB-USDC'),
        ('ARK/USDC:USDC', 'ARK-USDC'),
        ('ATOM/USDC:USDC', 'ATOM-USDC'),
        ('AVAX/USDC:USDC', 'AVAX-USDC'),
        ('BADGER/USDC:USDC', 'BADGER-USDC'),
        ('BANANA/USDC:USDC', 'BANANA-USDC'),
        ('BCH/USDC:USDC', 'BCH-USDC'),
        ('BIGTIME/USDC:USDC', 'BIGTIME-USDC'),
        ('BLUR/USDC:USDC', 'BLUR-USDC'),
        ('BLZ/USDC:USDC', 'BLZ-USDC'),
        ('BNB/USDC:USDC', 'BNB-USDC'),
        ('BNT/USDC:USDC', 'BNT-USDC'),
        ('BOME/USDC:USDC', 'BOME-USDC'),
        ('BSV/USDC:USDC', 'BSV-USDC'),
        ('BTC/USDC:USDC', 'BTC-USDC'),
        ('CAKE/USDC:USDC', 'CAKE-USDC'),
        ('CANTO/USDC:USDC', 'CANO-USDC'),
        ('CFX/USDC:USDC', 'CFX-USDC'),
        ('COMP/USDC:USDC', 'COMP-USDC'),
        ('CRV/USDC:USDC', 'CRV-USDC'),
        ('CYBER/USDC:USDC', 'CYBER-USDC'),
        ('DOGE/USDC:USDC', 'DOGE-USDC'),
        ('DOT/USDC:USDC', 'DOT-USDC'),
        ('DYDX/USDC:USDC', 'DYDX-USDC'),
        ('DYM/USDC:USDC', 'DYM-USDC'),
        ('ENA/USDC:USDC', 'ENA-USDC'),
        ('ENS/USDC:USDC', 'ENS-USDC'),
        ('ETC/USDC:', 'ETC-USDC'),
        ('ETH/USDC:USDC', 'ETH-USDC'),
        ('ETHFI/USDC:USDC', 'ETHFI-USDC'),
        ('FET/USDC:USDC', 'FET-USDC'),
        ('FIL/USDC:USDC', 'FIL-USDC'),
        ('FRIEND/USDC:USDC', 'FRIEND-USDC'),
        ('FTM/USDC:USDC', 'FTM-USDC'),
        ('FTT/USDC:USDC', 'FTT-USDC'),
        ('FXS/USDC:USDC', 'FXS-USDC'),
        ('GALA/USDC:USDC', 'GALA-USDC'),
        ('GAS/USDC:USDC', 'GAS-USDC'),
        ('GMT/USDC:USDC', 'GMT-USDC'),
        ('GMX/USDC:USDC', 'GMX-USDC'),
        ('HPOS/USDC:USDC', 'HPOS-USDC'),
        ('ILV/USDC:USDC', 'ILV-USDC'),
        ('IMX/USDC:USDC', 'IMX-USDC'),
        ('INJ/USDC:USDC', 'INJ-USDC'),
        ('JTO/USDC:USD', 'JTO-USDC'),
        ('JUP/USDC:USDC', 'JUP-USDC'),
        ('KAS/USD:USDC', 'KAS-USDC'),
        ('LDO/USDC:USDC', 'LDO-USDC'),
        ('LINK/USDC:USDC', 'LINK-USDC'),
        ('LOOM/USDC:USDC', 'LOOM-USDC'),
        ('LTC/USDC:USDC', 'LTC-USDC'),
        ('MANTA/USDC:USDC', 'MANTA-USDC'),
        ('MATIC/USDC:USDC', 'MATIC-USDC'),
        ('MAV/USDC:USDC', 'MAV-USDC'),
        ('MAVIA/USDC:USDC', 'MAVIA-USDC'),
        ('MEME/USDC:USDC', 'MEME-USDC'),
        ('MINA/USDC:USDC', 'MINA-USDC'),
        ('MKR/USDC:USDC', 'MKR-USDC'),
        ('MNT/USDC:USDC', 'MNT-USDC'),
        ('MYRO/USDC:USDC', 'MYRO-USDC'),
        ('NEAR/USDC:USDC', 'NEAR-USDC'),
        ('NEO/USDC:USDC', 'NEO-USDC'),
        ('NFTI/USDC:USDC', 'NFTI-USDC'),
        ('NTRN/USDC:USDC', 'NTRN-USDC'),
        ('OGN/USDC:USDC', 'OGN-USDC'),
        ('ONDO/USDC:USDC', 'ONDO-USDC'),
        ('OP/USDC:USDC', 'OP-USDC'),
        ('ORBS/USDC:USDC', 'ORBS-USDC'),
        ('ORDI/USDC:USDC', 'ORDI-USDC'),
        ('OX/USDC:USDC', 'OX-USDC'),
        ('PANDORA/USDC:USDC', 'PANDORA-USDC'),
        ('PENDLE/USDC:USDC', 'PENDLE-USDC'),
        ('PEOPLE/USDC:USDC', 'PEOPLE-USDC'),
        ('PIXEL/USDC:USDC', 'PIXEL-USDC'),
        ('POLYX/USDC:USDC', 'POLYX-USDC'),
        ('PYTH/USDC:USDC', 'PYTH-USDC'),
        ('RDNT/USDC:USDC', 'RDNT-USDC'),
        ('REQ/USDC:USDC', 'REQ-USDC'),
        ('RLB/USDC:USDC', 'RLB-USDC'),
        ('RNDR/USDC:USDC', 'RNDR-USDC'),
        ('RSR/USDC:USDC', 'RSR-USDC'),
        ('RUNE/USDC:USDC', 'RUNE-USDC'),
        ('SEI/USDC:USDC', 'SEI-USDC'),
        ('SHIA/USDC:USDC', 'SHIA-USDC'),
        ('SNX/USDC:USDC', 'SNX-USDC'),
        ('SOL/USDC:USDC', 'SOL-USDC'),
        ('STG/USDC:USDC', 'STG-USDC'),
        ('STRAX/USDC:USDC', 'STRAX-USDC'),
        ('STRK/USDC:USDC', 'STRK-USDC'),
        ('STX/USDC:USDC', 'STX-USDC'),
        ('SUI/USDC:USDC', 'SUI-USDC'),
        ('SUPER/USDC:USDC', 'SUPER-USDC'),
        ('SUSHI/USDC:USDC', 'SUSHI-USDC'),
        ('TAO/USDC:USDC', 'TAO-USDC'),
        ('TIA/USDC:USDC', 'TIA-USDC'),
        ('TNSR/USDC:USDC', 'TNSR-USDC'),
        ('TON/USDC:USDC', 'TON-USDC'),
        ('TRB/USDC:USDC', 'TRB-USDC'),
        ('TRX/USDC:USDC', 'TRX-USDC'),
        ('UMA/USDC:USDC', 'UMA-USDC'),
        ('UNI/USDC:USDC', 'UNI-USDC'),
        ('UNIBOT/USDC:USDC', 'UNIBOT-USDC'),
        ('USTC/USDC:USDC', 'USTC-USDC'),
        ('W/USDC:USDC', 'W-USDC'),
        ('WIF/USDC:', 'WIF-USDC'),
        ('WLD/USDC:USDC', 'WLD-USDC'),
        ('XAI/USDC:USDC', 'XAI-USDC'),
        ('XRP/USDC:USDC', 'XRP-USDC'),
        ('YGG/USDC:', 'YGG-USDC'),
        ('ZEN/USDC:USDC', 'ZEN-USDC'),
        ('ZETA/USDC:USDC', 'ZETA-USDC'),
        ('ZRO/USDC:USDC', 'ZRO-USDC'),
        ('kBONK/USDC:USDC', 'kBONK-USDC'),
        ('kFLOKI/USDC:USDC', 'kFLOKI-USDC'),
        ('kLUNC/USDC:USDC', 'kLUNC-USDC'),
        ('kPEPE/USDC:USDC', 'kPEPE-USDC'),
        ('kSHIB/USDC:USDC', 'kSHIB-USDC'),

    ]

    TIMEFRAME_CHOICES = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('15m', '15 Minutes'),
        ('30m', '30 Minutes'),
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
        ('1w', '1 Week'),
        ('1M', '1 Month'),
        # Add more timeframes as needed
    ]

    exchange_id = forms.ChoiceField(choices=EXCHANGE_CHOICES, label="Exchange")
    symbol = forms.MultipleChoiceField(choices=SYMBOL_CHOICES, label="Symbol")
    timeframe = forms.MultipleChoiceField(choices=TIMEFRAME_CHOICES, label="Timeframe")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                                 initial=datetime.now().replace(day=1).strftime('%Y-%m-%d'))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                               initial=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
