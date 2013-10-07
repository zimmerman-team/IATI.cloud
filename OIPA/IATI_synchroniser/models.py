from django.db import models
import datetime
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from IATI_synchroniser.dataset_syncer import DatasetSyncer
from IATI_synchroniser.codelist_importer import CodeListImporter
from IATI.parser import Parser



INTERVAL_CHOICES = (
    (u'YEARLY', _(u"Parse yearly")),
    (u'MONTHLY', _(u"Parse monthly")),
    (u'WEEKLY', _(u"Parse weekly")),
    (u'DAILY', _(u"Parse daily")),
)
class Publisher(models.Model):
    org_name = models.CharField(max_length=255)
    org_abbreviate = models.CharField(max_length=55, blank=True, null=True)
    default_interval = models.CharField(verbose_name=_(u"Interval"), max_length=55, choices=INTERVAL_CHOICES, default=u'MONTHLY')

    def __unicode__(self):
        if self.org_abbreviate:
            return self.org_abbreviate
        return self.org_name

    class Meta:
        ordering = ["org_name"]


class iati_xml_source(models.Model):
    TYPE_CHOICES = (
        (1, _(u"Activity Files")),
        (2, _(u"Organisation Files")),
    )
    ref = models.CharField(verbose_name=_(u"Reference"), max_length=70, help_text=_(u"Reference for the XML file. Preferred usage: 'collection' or single country or region name"))
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    publisher = models.ForeignKey(Publisher)
    source_url = models.URLField(unique=True, help_text=_(u"Hyperlink to an IATI activity or organisation XML file."))
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["ref"]

    def __unicode__(self):
        return self.ref

    def get_parse_status(self):
        return mark_safe("<img class='loading' src='/static/img/loading.gif' alt='loading' style='display:none;' /><a data-xml='xml_%i' class='parse'><img src='/static/img/utils.parse.png' style='cursor:pointer;' /></a>") % self.id
    get_parse_status.allow_tags = True
    get_parse_status.short_description = _(u"Parse status")

    def process(self, verbosity, save=True):

        parser = Parser()
        parser.parse_url(self.source_url, self.ref)

        if save:
            self.save()

    def save(self, *args, **kwargs):
        if not self.id:
            self.process(verbosity=1, save=False)
        super(iati_xml_source, self).save()



class dataset_sync(models.Model):
    TYPE_CHOICES = (
        (1, _(u"Activity Files")),
        (2, _(u"Organisation Files")),
        )

    interval = models.CharField(verbose_name=_(u"Interval"), max_length=55, choices=INTERVAL_CHOICES)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)

    def __unicode__(self):
        return self.interval

    class Meta:
        verbose_name_plural = "dataset synchronisers"

    def sync_now(self):
        return mark_safe("<img class='loading' src='/static/img/loading.gif' alt='loading' style='display:none;' /><a data-sync='sync_%i' class='sync    '><img src='/static/img/utils.parse.png' style='cursor:pointer;' /></a>") % self.id
    sync_now.allow_tags = True
    sync_now.short_description = _(u"Sync now?")

    def _add_month(self, d,months=1):
        year, month, day = d.timetuple()[:3]
        new_month = month + months
        return datetime.date(year + ((new_month-1) / 12), (new_month-1) % 12 +1, day)

    def process(self):
        if self.interval == u'YEARLY' and (self._add_month(self.date_updated, 12) <= datetime.datetime.now().date()):
            self.sync_dataset_with_iati_api()
        elif self.interval == u'MONTHLY' and (self._add_month(self.date_updated) <= datetime.datetime.now().date()):
            self.sync_dataset_with_iati_api()
        elif self.interval == u'WEEKLY' and (self.date_updated+datetime.timedelta(7) <= datetime.datetime.today()):
            self.sync_dataset_with_iati_api()
        elif self.interval == u'DAILY' and (self.date_updated+datetime.timedelta(1) <= datetime.datetime.today()):
            self.sync_dataset_with_iati_api()

    def sync_dataset_with_iati_api(self):
        syncer = DatasetSyncer()
        syncer.synchronize_with_iati_api(self.type)



class codelist_sync(models.Model):

    date_updated = models.DateTimeField(auto_now=True, editable=False)


    class Meta:
        verbose_name_plural = "codelist synchronisers"

    def sync_now(self):
        return mark_safe("<img class='loading' src='/static/img/loading.gif' alt='loading' style='display:none;' /><a data-sync='sync_%i' class='sync    '><img src='/static/img/utils.parse.png' style='cursor:pointer;' /></a>") % self.id
    sync_now.allow_tags = True
    sync_now.short_description = _(u"Sync now?")

    def sync_codelist(self):
        syncer = CodeListImporter()
        syncer.synchronise_with_codelists();