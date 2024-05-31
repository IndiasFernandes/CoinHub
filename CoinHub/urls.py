from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from .views import DashboardView, AboutView, activate_ssh

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('bots/', include(('apps.bots.urls', 'bots'), namespace='bots')),
    path('exchanges/', include(('apps.exchanges.urls', 'exchanges'), namespace='exchanges')),
    path('about/', AboutView.as_view(), name='about'),
    path('market/', include(('apps.market.urls', 'market'), namespace='market')),
    path('activate-ssh/', activate_ssh, name='activate_ssh'),
    path('app_gytis/', include('app_gytis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)