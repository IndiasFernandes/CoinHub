from django import forms
from .models import Bot, Strategy, Exchange, Market

class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ['exchange', 'market', 'strategy', 'is_active']
        widgets = {
            'strategy': forms.Select(),
            'exchange': forms.Select(),
            'market': forms.Select(),
            'is_active': forms.CheckboxInput(),
        }