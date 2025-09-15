from django.apps import AppConfig
from django.utils.translation import ngettext_lazy as _


class PlantConfig(AppConfig):
    name = 'plant'
    verbose_name = _('plant', 'plants', 2)
