# CoinHub/settings.py
import os
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

ENV = os.getenv('DJANGO_SETTINGS_MODULE')

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



if ENV == 'CoinHub.settings_development':
    from .settings_development import *
elif ENV == 'CoinHub.settings_production':
    from .settings_production import *
else:
    raise Exception("DJANGO_SETTINGS_MODULE is not set or is set incorrectly")
