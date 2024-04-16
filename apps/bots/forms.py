from django import forms
from .models import Bot, Strategy, Exchange, Market

class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = [
            'name', 'user', 'exchange', 'market', 'strategy', 'balance',
            'initial_balance', 'max_drawdown', 'max_drawdown_percentage',
            'st_value', 'stop_loss', 'loop_interval', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'exchange': forms.Select(attrs={'class': 'form-control'}),
            'market': forms.Select(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_drawdown': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_drawdown_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'st_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-control'}),
            'loop_interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }

class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'strategy_type', 'position', 'logic', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'strategy_type': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'logic': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
