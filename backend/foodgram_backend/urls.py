from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api import utils

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('<str:short_url>', utils.redirection),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
