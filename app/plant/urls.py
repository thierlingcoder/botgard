from django.conf.urls import url

from . import views

app_name = "plant"
urlpatterns = [
    url(r'^available/(?P<forId>\d+)$',      views.is_available, name='is_available'),

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
