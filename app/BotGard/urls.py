from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from config_tables.admin import ConfigurableTable
from botman.views import index_page
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Serious Seeds API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="serious@hardwarepunk.de"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),

    url(r'^individual/',    include('individuals.urls')),
    url(r'^seeds/',         include('seeds.urls')),
    url(r'^botman/',        include('botman.urls')),
    url(r'^$',              index_page, name="index"),
    url(r'^plant/',         include('plant.urls')),
    url(r'^seedcatalog/',   include('seedcatalog.urls')),
    url(r'^tickets/',       include('tickets.urls')),
    url(r'^labels/',        include('labels.urls')),
    url(r'^sidebar/',       include('sidebar.urls')),
    url(r'^ajax/',          include('ajax.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
)

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

