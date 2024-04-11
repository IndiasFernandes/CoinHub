from django.urls import path
from .views import exchange_list, exchange_detail, exchange_new, chart_view, update_market_coins

app_name = 'exchange'  # This line is crucial for namespacing to work

urlpatterns = [
    path('list/', exchange_list, name='exchange_list'),
    path('<int:exchange_id>/', exchange_detail, name='exchange_detail'),
    path('new/', exchange_new, name='exchange_new'),
    path('chart/', chart_view, name='chart_view'),
    path('market/<int:market_id>/update_coins/', update_market_coins, name='update_market_coins'),
    # Add other exchange-related URL patterns here
]