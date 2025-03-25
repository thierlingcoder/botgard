from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms

from config_tables.admin import Configurable, configurable
from ajax.autocomplete import AutoCompleteForm
from tools import global_request

PROTECTION_OF_SPECIES_CHOICES = (
    ('LC', 'LC (Least Concern)'),
    ('NT', 'NT (Near Threatened)'),
    ('VU', 'VU (Vulnerable)'),
    ('EN', 'EN (Endangered)'),
    ('CR', 'CR (Critically Endangered)'),
    ('EW', 'EW (Extinct in the wild)'),
    ('EX', 'EX (Extinct)'),
)

LIFEFORM_CHOICES = (
    ('P', 'Phanerophyt (Gehölz)'),
    ('C', 'Chamaephyt (Zwergstrauch/Halbstrauch)'),
    ('H', 'Hemikryptophyt (Staude)'),
    ('K', 'Kryptophyt'),
    ('T', 'Therophyt (Einjährige)'),
)


class Category(models.Model, Configurable):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('category',)
        unique_together = ('category',)

    _id_field = "category"

    category = models.CharField(verbose_name=_('category'), max_length=50, blank=False)
    full_name_generated = models.CharField(verbose_name=_('full name'), max_length=350, blank=True)

    @configurable
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '%s' % (self.category)

    @configurable

    def change_link_decorator(self):
        url = reverse("admin:plant_category_change", args=(self.pk,))
        return mark_safe('<a href="%s" class="changelink">%s</a>' % (url, _('show')))
    change_link_decorator.short_description = _('show')
    change_link_decorator.exclude_csv = True

    @configurable
    def delete_link_decorator(self):
        url = reverse("admin:plant_category_delete", args=(self.pk,))
        return mark_safe('<a href="%s" class="deletelink">%s</a>' % (url, _('delete')))
    delete_link_decorator.short_description = _('delete')
    delete_link_decorator.exclude_csv = True

    def save(self, *args, **kwargs):
        if hasattr(self, "full_name_generated"):
            self.full_name_generated = self.get_full_name()
        super(Category, self).save(*args, **kwargs)
        # update coresponding Plant.full_name_generated
        if hasattr(Plant, "full_name_generated"):
            for i in Plant.objects.filter(category=self):
                i.save()


class CategoryForm(AutoCompleteForm(Category)):
    pass


class Plant(models.Model, Configurable):

    class Meta:
        verbose_name = ungettext_lazy('plant', 'plants', 1)
        verbose_name_plural = ungettext_lazy('plant', 'plants', 2)
        ordering = ('category__category', 'collective_species', 'plant',)
        unique_together = (
            "category", "collective_species", "plant", "cultivar",
        )
        permissions = (("can_check_nomenclature", _("can check nomenclature of a plant")),)

    _id_field = 'full_name_generated'

    category = models.ForeignKey(Category, verbose_name=_('category'), on_delete=models.CASCADE)
    plant = models.CharField(verbose_name=_('plant'), max_length=100, blank=False, default="")
    collective_species = models.CharField(verbose_name=_('collective_species'), max_length=100, blank=True)
    cultivar = models.CharField(verbose_name=_('cultivar / breed'), max_length=200, blank=True,
                                help_text=_('without quotation marks'))
    full_name_generated = models.CharField(max_length=200, verbose_name=_("full name"), blank=True)
    synonyme = models.TextField(verbose_name=_('synonyms'), blank=True, null=True)
    comment = models.TextField(verbose_name=_('comment'), max_length=10000, blank=True, null=True)
    picture = models.ImageField(verbose_name=_('picture'), upload_to="pictures", blank=True)

    @configurable
    def __str__(self):
        return self.full_name()

    def full_name(self, with_author=True):
        return_string = '%s' % (self.plant)
        if self.collective_species:
            return_string = self.collective_species + " - " + self.plant
        if self.cultivar:
            return_string += " \'" + self.cultivar + "\'"
        return return_string
    full_name.template_doc = _("Full plant name")

    def distribution_lines(self):
        return self.area_of_distribution_etikettxt.split("\n")
    distribution_lines.template_doc = _(
        "Area of distribution (each line separate, access with {{obj.plant.distribution_lines.0}}"
        ", {{obj.plant.distribution_lines.0}}, aso...)"
    )

    @configurable
    def category_single(self):
        return self.category.category
    category_single.short_description = _('category')
    category_single.admin_order_field = "category__category"

    @configurable
    def change_link_decorator(self):
        url = reverse("admin:plant_plant_change", args=(self.pk,))
        return mark_safe('<a href="%s" class="changelink">%s</a>' % (url, _('show')))
    change_link_decorator.short_description = _('show')
    change_link_decorator.exclude_csv = True

    @configurable
    def delete_link_decorator(self):
        url = reverse("admin:plant_plant_delete", args=(self.pk,))
        return mark_safe('<a href="%s" class="deletelink">%s</a>' % (url, _('delete')))
    delete_link_decorator.short_description = _('delete')
    delete_link_decorator.exclude_csv = True

    @configurable
    def availability_decorator(self):
        url = reverse("plant:is_available", args=(self.pk,))
        return mark_safe('<a href="%s">%s</a>' % (url, _('check')))
    availability_decorator.short_description = _('availability')
    availability_decorator.exclude_csv = True

    @configurable
    def search_individuals_link_decorator(self):
        url = reverse("admin:individuals_individual_changelist")
        return mark_safe('<a href="%s?q=%s%%20%s">%s</a>' % (
            url,
            self.category.category, self.plant, _('search individuals')
        ))
    search_individuals_link_decorator.short_description = _('individuals')
    search_individuals_link_decorator.exclude_csv = True

    @configurable
    def search_seeds_link_decorator(self):
        url = reverse("admin:individuals_seed_changelist")
        return mark_safe('<a href="%s?q=%s%%20%s&seed_available__exact=1">%s</a>' % (
            url,
            self.category.category, self.plant, _('search seeds')
        ))
    search_seeds_link_decorator.short_description = _('seeds')
    search_seeds_link_decorator.exclude_csv = True

    @configurable
    def alive_individuals_decorator(self):
        has_individuals = (
            self.__class__.objects
                .filter(pk=self.pk, individual__is_alive_generated=True)
                .exists()
        )
        return mark_safe('<span class="icon-%s"></span>' % (
            "yes" if has_individuals else "no",
        ))
    alive_individuals_decorator.short_description = _('alive individuals')

    def save(self, *args, **kawrgs):
        if hasattr(self, "full_name_generated"):
            self.full_name_generated = self.full_name()
        super(Plant, self).save(*args, **kawrgs)

        from individuals.models import Individual
        if hasattr(Individual, "id_name_generated"):
            for i in Individual.objects.filter(plant=self):
                i.save()


class PlantForm(AutoCompleteForm(Plant)):
    def __init__(self, *args, **kwargs):
        super(PlantForm, self).__init__(*args, **kwargs)
        if not global_request.get_current_user().has_perm("plant.can_check_nomenclature"):
            self.fields["nomenclature_checked"] = forms.NullBooleanField(disabled=True)
