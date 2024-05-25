import os
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoinHub.settings')

application = get_asgi_application()
