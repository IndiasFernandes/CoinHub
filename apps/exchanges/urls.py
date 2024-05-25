from django.urls import path
from .views import exchange_list, exchange_detail, exchange_new, chart_view, update_market_coins, download_data_view, \
    get_exchange_data, add_market

app_name = 'exchange'

urlpatterns = [
    path('list/', exchange_list, name='exchange_list'),
    path('<int:exchange_id>/', exchange_detail, name='exchange_detail'),
    path('new/', exchange_new, name='exchange_new'),
    path('chart/', chart_view, name='chart_view'),
    path('update_coins/<int:market_id>/', update_market_coins, name='update_market_coins'),
    path('download/', download_data_view, name='download_data'),
    path('add-market/<int:exchange_id>/', add_market, name='add_market'),
    path('<str:exchange_id_char>/data/', get_exchange_data, name='get_exchange_data'),

]
