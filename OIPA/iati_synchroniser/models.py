from django.db import models
import datetime
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from iati_synchroniser.dataset_syncer import DatasetSyncer
from iati.parser import Parser
from iati.deleter import Deleter

INTERVAL_CHOICES = (
    (u'YEARLY', _(u"Parse yearly")),
    (u'MONTHLY', _(u"Parse monthly")),
    (u'WEEKLY', _(u"Parse weekly")),
    (u'DAILY', _(u"Parse daily")),
)

class Publisher(models.Model):
    org_id = models.CharField(max_length=100)
    org_abbreviate = models.CharField(max_length=55)
    org_name = models.CharField(max_length=255)
    default_interval = models.CharField(verbose_name=_(u"Interval"), max_length=55, choices=INTERVAL_CHOICES, default=u'MONTHLY')
    XML_total_activity_count = models.IntegerField(null=True, default=None)
    OIPA_total_activity_count = models.IntegerField(null=True, default=None)

    def __unicode__(self):
        return self.org_id


class IatiXmlSource(models.Model):
    TYPE_CHOICES = (
        (1, _(u"Activity Files")),
        (2, _(u"Organisation Files")),
    )
    INTERVAL_CHOICES = (
        ("day", _(u"Day")),
        ("week", _(u"Week")),
        ("month", _(u"Month")),
        ("year", _(u"Year")),
    )
    ref = models.CharField(verbose_name=_(u"Reference"), max_length=70, help_text=_(u"Reference for the XML file. Preferred usage: Name on IATI registry"))
    title = models.CharField(max_length=255)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    publisher = models.ForeignKey(Publisher)
    source_url = models.CharField(max_length=255, unique=True, help_text=_(u"Hyperlink to an iati activity or organisation XML file."))
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now_add=True, editable=False)
    update_interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default="month")
    last_found_in_registry = models.DateTimeField(default=None, null=True)
    xml_activity_count = models.IntegerField(null=True, default=None)
    oipa_activity_count = models.IntegerField(null=True, default=None)
    iati_standard_version = models.CharField(max_length=10, default="")
    is_parsed = models.BooleanField(null=False, default=False)
    added_manually = models.BooleanField(null=False, default=True)

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["ref"]

    def __unicode__(self):
        return self.ref

    def get_parse_status(self):
        return mark_safe("<a data-xml='xml_%i' class='parse-btn'>Parse</a>") % self.id
    get_parse_status.allow_tags = True
    get_parse_status.short_description = _(u"Parse status")

    def process(self):
        self.is_parsed = True
        parser = Parser()
        parser.parse_url(self.source_url, self.ref)
        self.date_updated = datetime.datetime.now()
        self.save(process=False)
        from iati_synchroniser.parse_admin import ParseAdmin
        activity_counter = ParseAdmin()
        # self.xml_activity_count = activity_counter.get_xml_activity_amount(self.source_url)
        # self.oipa_activity_count = activity_counter.get_oipa_activity_amount(self.ref)
        self.save(process=False)

    def save(self, process=True, added_manually=True, *args, **kwargs):
        self.added_manually = added_manually
        super(IatiXmlSource, self).save()
        if process:
            self.process()

    def delete(self, process=True, *args, **kwargs):
        deleter = Deleter()
        deleter.delete_by_source(self.source_url)
        super(IatiXmlSource, self).delete()





class Codelist(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    description = models.TextField( max_length=1000, blank=True, null=True)
    count = models.CharField(max_length=10, blank=True, null=True)
    fields = models.CharField(max_length=255, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self,):
        return "%s" % (self.name)