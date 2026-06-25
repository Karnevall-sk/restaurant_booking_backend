from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('restaurants.urls')),
    path('api/v1/', include('menu.urls')),
    path('api/v1/', include('reservations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]