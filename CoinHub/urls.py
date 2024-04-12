"""
URL configuration for CoinHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from .views import dashboard_view, about_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('accounts/', include(('apps.accounts.urls', 'apps.accounts'), namespace='accounts')),
    path('bots/', include(('apps.bots.urls', 'apps.bots'), namespace='bots')),
    path('exchanges/', include(('apps.exchanges.urls', 'apps.exchanges'), namespace='exchanges')),
    path('about/', about_view, name='about'),
    path('market/', include(('apps.market.urls', 'apps.market'), namespace='market')),

]