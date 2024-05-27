from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'market'

    def ready(self):
        import CoinHub.signals

class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.market'
