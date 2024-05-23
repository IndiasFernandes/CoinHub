# CoinHub/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv('DJANGO_SETTINGS_MODULE')

if ENV == 'CoinHub.settings_development':
    from .settings_development import *
elif ENV == 'CoinHub.settings_production':
    from .settings_production import *
else:
    raise Exception("DJANGO_SETTINGS_MODULE is not set or is set incorrectly")
