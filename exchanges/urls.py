from django.urls import path
from .views import exchange_list, exchange_detail, exchange_new

app_name = 'exchange'  # This line is crucial for namespacing to work

urlpatterns = [
    path('list/', exchange_list, name='exchange_list'),
    path('<int:exchange_id>/', exchange_detail, name='exchange_detail'),
    path('new/', exchange_new, name='exchange_new'),
    # Add other exchange-related URL patterns here
]