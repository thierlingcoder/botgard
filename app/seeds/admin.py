import re
from typing import List, Type

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
from django.db import transaction

from .models import *
from plantimages.admin import PlantImageInline

from tools import readOnlyAdmin
from tools.search_fields import search_fields_compatible
from config_tables.admin import ConfigurableTable, ForeignKeyFilter
from ajax.autocomplete import AutoCompleteForm
from labels.mass_action import add_label_mass_actions



class SeedsAdmin(readOnlyAdmin.ReadPermissionModelAdmin, ConfigurableTable):
    form = SeedsForm
    save_on_top = True
    actions_on_top = True
    list_display = (
        'change_link_decorator', 'category', 'plant', 'id_container', 'source', 'collection_year')
    list_filter = (
                   ('plant__full_name_generated', ForeignKeyFilter),
                   ('plant__category__category', ForeignKeyFilter),
                   )

    blacklist = ('id', '__str__', 'creation_date')

    search_fields = search_fields_compatible([
        'id_container', '@plant__plant', 'source',
    ])
    ordering = ('id_container',)
    fieldsets = (
        (None, {
            'fields': (('id_container', 'seed_available', 'seed_in_stock',),
                       ('plant', 'species_checked_by', 'came_as_species'),)
        }),
    )

    class Media:
        css = {"screen": ('BotGard/css_dropdown/css_dropdown.css',)}

    def get_search_results(self, request, queryset, search_term):
        order_ids = get_seed_order_ids(search_term)
        if not order_ids:
            return super().get_search_results(request, queryset, search_term)

        return queryset.filter(order_number__in=order_ids), False

    def get_actions(self, request):
        actions = super().get_actions(request)
        add_label_mass_actions(request, actions, "individual")
        return actions


def get_seed_order_ids(s: str) -> List[str]:
    return re.findall(r"\d+", s)


admin.site.register(Seeds, SeedsAdmin)
