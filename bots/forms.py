from django import forms
from .models import Bot, Strategy, Exchange, Market

class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ['name', 'exchange', 'market', 'strategy', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(),
            'exchange': forms.Select(),
            'market': forms.Select(),
            'is_active': forms.CheckboxInput(),
        }