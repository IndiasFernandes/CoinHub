from django.urls import path
from .views import login_view, logout_view, register_view

app_name = 'accounts'  # This line is optional if you are using the namespace argument in include()

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    # Other accounts URLs...
]
