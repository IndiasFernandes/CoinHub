from django.apps import AppConfig

class MarketConfig(AppConfig):
    name = 'apps.market'

    def ready(self):
        import apps.market.signals  # Correct path to where your signals are defined


class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.market'
