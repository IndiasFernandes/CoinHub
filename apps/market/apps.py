from django.apps import AppConfig

class MarketConfig(AppConfig):
    name = 'apps.market'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import apps.market.signals  # Ensure this is the path to your signals module
