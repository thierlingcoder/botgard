from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy as __
from config_tables.admin import Configurable, configurable
from ajax.autocomplete import AutoCompleteForm

from plant.models import Plant, Category


class Seeds(models.Model, Configurable):

    class Meta:
        verbose_name = _("seed")
        verbose_name_plural = _("seeds")
        unique_together = ("plant", "id_container", "source", "collection_year")

    _id_field = "id_name_generated"

    plant = models.ForeignKey('plant.Plant', verbose_name=_("Plant"), blank=False, on_delete=models.CASCADE)
    id_container = models.CharField(max_length=100, verbose_name=_("container"), blank=False)
    source = models.CharField(max_length=100, verbose_name=_("source"), blank=True)
    collection_year = models.IntegerField(verbose_name=_("collection_year"), blank=True)
    creation_date = models.DateField(verbose_name=_("creation_date"), blank=True, null=True)


    # source = models.ForeignKey('botman.BotanicGarden', related_name="source_key", verbose_name=_("source"), blank=True,
    #                            null=True, on_delete=models.CASCADE)

    is_alive_generated = models.BooleanField(verbose_name=_("is alive"), editable=False, default=False)

    @configurable
    def __str__(self):
        return self.id_name_generated
    __str__.admin_order_field = 'id_name_generated'
    __str__.short_description = _('Seeds')

    def calc_outplantings(self, do_save=True):
        """
        Calculate and store the following fields:
        - outplantings_generated
        - alive_outplantings_generated
        - departments_generated
        - territories_generated
        - is_alive_generated
        """
        from .outplanting import Outplanting
        locations = Outplanting.objects.filter(individual=self.pk)
        locations_alive = locations.filter(plant_died=None)

        self.outplantings_generated = [t[0] for t in locations.values_list("id")]
        self.alive_outplantings_generated = [t[0] for t in locations_alive.values_list("id")]
        self.departments_generated = " ".join(sorted(set(
            l.department.full_code for l in locations if l.department)))
        self.territories_generated = " ".join("(%s)" % i for i in
                                              sorted(set(l.department.territory.code for l in locations if l.department and l.department.territory)))
        self.is_alive_generated = locations_alive.count() > 0
        if do_save:
            self.save()

    def get_outplantings(self, alive_only=True):
        """Returns list of belonging Outplanting instances from database-cache"""
        from .outplanting import Outplanting
        ids = self.alive_outplantings_generated if alive_only else self.outplantings_generated
        if not ids:
            return []
        outpl = []
        for id in ids:
            try:
                outpl.append(Outplanting.objects.get(pk=id))
            except Outplanting.DoesNotExist:
                pass
        return outpl

    def _get_departments_html(self):
        links = []
        deps = {elem.department.full_code: elem.department
                for elem in self.get_outplantings(alive_only=False)
                if elem.department}
        #print(self.get_outplantings(alive_only=True))
        for code in sorted(deps):
            department = deps[code]
            url = reverse("admin:individuals_department_change", args=(department.pk,))
            links.append('<a href="%s" title="%s">%s</a> ' % (
                url, department.name, department.full_code.replace(" ", "&nbsp;")))
        return mark_safe("<br/>\n".join(links))

    def _get_territories_html(self):
        links = []
        deps = {elem.department.territory.code: elem.department.territory
                for elem in self.get_outplantings(alive_only=False)
                if elem.department and elem.department.territory}
        for code in sorted(deps):
            territory = deps[code]
            url = reverse("admin:individuals_territory_change", args=(territory.pk,))
            links.append('<a href="%s" title="%s">%s</a> ' % (
                url, territory.name, territory.code.replace(" ", "&nbsp;")))
        return mark_safe("<br/>\n".join(links))

    @configurable
    def change_link_decorator(self):
        return _("show")

    change_link_decorator.short_description = _("show")
    change_link_decorator.exclude_csv = True

    @configurable
    def delete_link_decorator(self):
        url = reverse("admin:individuals_individual_delete", args=(self.pk,))
        return mark_safe('<a href="%s" class="deletelink">%s</a>' % (url, _("delete")))

    delete_link_decorator.short_description = _("delete")
    delete_link_decorator.exclude_csv = True

    @configurable
    def etikett_link_decorator(self):
        from labels import label_link_decorator
        return label_link_decorator(
            "individual", self.pk, self.ipen_generated
        )

    etikett_link_decorator.short_description = _("create label")
    etikett_link_decorator.exclude_csv = True

    @configurable
    def plant_link_decorator(self):
        url = reverse("admin:plant_plant_change", args=(self.plant.pk,))
        return mark_safe('<a href="%s">%s</a>' % (url, self.plant))
    plant_link_decorator.short_description = __("plant", "plants", 1)
    plant_link_decorator.admin_order_field = "plant"
    # redirection to field for filter-list
    # can also be a non-foreign field
    plant_link_decorator.searchable_field = "plant__full_name_generated"

    @configurable
    def category_single(self):
        return self.plant.category.category
    category_single.short_description = _('category')
    category_single.admin_order_field = "plant__category__category"

    @configurable
    def departments_decorator(self):
        return self._get_departments_html()
    departments_decorator.short_description = _("departments")
    departments_decorator.admin_order_field = "departments_generated"

    @configurable
    def territories_decorator(self):
        return self._get_territories_html()
    territories_decorator.short_description = _("territories")
    territories_decorator.admin_order_field = "territories_generated"

    @configurable
    def nomenclature_checked_decorator(self):
        icon_url = static('admin/img/icon-%s.svg' %
                          {True: 'yes', False: 'no', None: 'unknown'}[self.plant.nomenclature_checked])
        return mark_safe(format_html('<img src="{}" alt="{}" />', icon_url, self.plant.nomenclature_checked))
    nomenclature_checked_decorator.short_description = _("nomenclature checked")
    nomenclature_checked_decorator.admin_order_field = "plant__nomenclature_checked"

    @configurable
    def etikett_text_decorator(self):
        return self.plant.area_of_distribution_etikettxt
    etikett_text_decorator.short_description = _("label text")
    etikett_text_decorator.admin_order_field = "plant__area_of_distribution_etikettxt"

    @configurable
    def etikett_detail_decorator(self):
        return self.plant.area_of_distribution_background
    etikett_detail_decorator.short_description = _("detailed")
    etikett_detail_decorator.admin_order_field = "plant__area_of_distribution_background"

    @configurable
    def is_alive(self):
        return mark_safe('<span class="icon-%s"></span>' % (
            "yes" if self.is_alive_generated else "no",
        ))
    is_alive.short_description = _("is alive")
    is_alive.admin_order_field = "is_alive_generated"

    @configurable
    def image_decorator(self):
        from plantimages.models import PlantImage
        from easy_thumbnails.files import get_thumbnailer
        from easy_thumbnails.exceptions import InvalidImageFormatError

        qset = PlantImage.objects.filter(individual=self)
        if not qset.exists():
            return ""
        image = qset.order_by("pk")[0]
        url = "%s%s" % (settings.MEDIA_URL, image.image)
        try:
            thumb_url = get_thumbnailer(image.image)['preview'].url
        except InvalidImageFormatError:
            return ""
        alt = image.comment
        return mark_safe('<a href="%s" title="%s" target="_blank"><img src="%s" alt="%s"/></a>' % (url, alt, thumb_url, alt))
    image_decorator.short_description = _("image")
    image_decorator.exclude_csv = True

    def plant_lines(self):
        """Special function to output a multiline string for use with labels"""
        spec_name = self.plant.full_name(with_author=False)

        line1 = ''
        line2 = ''

        split_index = spec_name.find("subsp.")

        if split_index >= 0:
            line1 = spec_name[0:split_index]
            line2 = spec_name[split_index:]
            return line1, line2

        spec_name = spec_name.split()

        if len(spec_name) == 2:
            line1 = self.plant.category.category
            line2 = self.plant.plant
        else:
            for elem in spec_name:
                if len(line1) < 15:
                    line1 += u" %s" % elem
                else:
                    line2 += u" %s" % elem
            line1 = line1[1:]
            line2 = line2[1:]

        #if line2 == self.plant.get_author_name():
        #    line2 = ""
        return line1, line2


    def save(self, *args, **kwargs):
        # -- update generated fields --

        # -- update id_name_generated --
        self.id_name_generated = (
            "%s (%s)" % (self.id_container, self.plant.full_name(with_author=False))
        )[:100]

        # -- save Individual --
        super(Seeds, self).save(*args, **kwargs)

class SeedsForm(AutoCompleteForm(Seeds)):
    pass