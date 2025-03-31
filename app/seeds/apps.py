from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SeedsConfig(AppConfig):
    name = 'seeds'
    verbose_name = _("Seeds and Storage")