from django.contrib import admin
from config_tables.admin import ConfigurableTable, configurable, ForeignKeyFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

from tools import readOnlyAdmin
from tools.search_fields import search_fields_compatible

from .models import *


class CategoryAdmin(readOnlyAdmin.ReadPermissionModelAdmin, ConfigurableTable):
    form = CategoryForm
    list_display = ('change_link_decorator', 'category', 'delete_link_decorator')
    search_fields = search_fields_compatible(
        ('category',)
    )
    fieldsets = (
        (None, {
            'fields': ('category',),
        }),
    )

    class Media:
        css = {"screen": (
            '/static/config_tables/searchable_admin_list.css',
            #'/static/config_tables/jquery-ui.min.css',
            )
        }
        js = (
            '/static/plant/asteraceae.js',
        )


class AliveIndividualsListFilter(admin.SimpleListFilter):
    title = _("alive individuals")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "individuals_exist"

    def lookups(self, request, model_admin):
        return [
            ("1", _("Exist")),
            ("0", _("Don't exist")),
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "1":
            return queryset.filter(
                individual__is_alive_generated=True,
            ).distinct()
        elif self.value() == "0":
            return queryset.exclude(
                individual__is_alive_generated=True,
            ).distinct()
        else:
            return queryset


class PlantAdmin(readOnlyAdmin.ReadPermissionModelAdmin, ConfigurableTable):
    form = PlantForm
    list_display = (
        'change_link_decorator', #'full_name_generated', '__str__',
        'category_single',
        'collective_species',
        'plant',
        'cultivar',
        'synonyme',
        'search_individuals_link_decorator', 'search_seeds_link_decorator', 'availability_decorator',
        'alive_individuals_decorator',
        'delete_link_decorator',
    )
    blacklist = ("id", "__str__")
    list_filter = (
        #'nomenclature_checked', 'poisonous_plant',
        ('category__full_name_generated', ForeignKeyFilter),
        ('category__category', ForeignKeyFilter),
        AliveIndividualsListFilter,
    )
    search_fields = search_fields_compatible(
        ['@category__category', '@plant', 'collective_species', 'synonyme',
         'cultivar', ]
    )
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': (
            'category',
            ('collective_species',),
            ('plant',),
            'cultivar', 'synonyme')
        }),
        (_('additional'), {
            'classes': 'collapse',
            'fields': (
            'picture', 'comment')
        }),
    )

    class Media:
        js = (
            '/static/plant/distribution_text.js',
        )


admin.site.register(Plant, PlantAdmin)
admin.site.register(Category, CategoryAdmin)
