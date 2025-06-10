from django.conf.urls import url
from django.urls import path, include
from .views import PlantModelViewSet, CategoryModelViewSet
from . import views

from rest_framework.routers import DefaultRouter


app_name = "plant"

router = DefaultRouter()

router.register(r"plants", PlantModelViewSet, basename="plant")
router.register(r"categories", CategoryModelViewSet, basename="category")

urlpatterns = [
    url(r'^available/(?P<forId>\d+)$',      views.is_available, name='is_available'),
    path("", include(router.urls)),

    # TODO: use or remove
    #url(r'^ajax/plant/autocomplete/(?P<search_item>\w+)/(?P<limit_by>\d+)$',
    #                                        views.ajax_autocomplete_species,    name='ajax_autocomplete_species'),
    #url(r'^ajax/families/autocomplete/(?P<search_item>\w+)/(?P<limit_by>\d+)$',
    #                                        views.ajax_autocomplete_families,   name='ajax_autocomplete_families'),
    #url(r'^ajax/individual/autocomplete/plant/(?P<limit_by>\d+)$',
    #                                        views.ajax_autocomplete_individual_species,
    #                                                                            name='ajax_autocomplete_individual_species'),
    #url(r'^ajax/plant/name/(?P<forId>\d+)$',
    #                                        views.ajax_name,                    name='ajax_name'),
]
