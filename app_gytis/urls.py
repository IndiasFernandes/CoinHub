from django.urls import path
from .views import process_file_view

app_name = 'app_gytis'

urlpatterns = [
    path('upload/', process_file_view, name='upload'),
]
