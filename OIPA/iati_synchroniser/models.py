from django.db import models
import datetime
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from iati.parser.iati_parser import ParseIATI
# from iati_synchroniser.parse_admin import ParseAdmin


class Publisher(models.Model):
    org_id = models.CharField(max_length=100)
    org_abbreviate = models.CharField(max_length=55, default="")
    org_name = models.CharField(max_length=255)
    default_interval = models.CharField(
        max_length=55,
        choices=(
            ('YEARLY', 'Parse yearly'),
            ('MONTHLY', 'Parse monthly'),
            ('WEEKLY', 'Parse weekly'),
            ('DAILY', 'Parse daily'),
        ),
        default='MONTHLY')
    XML_total_activity_count = models.IntegerField(null=True, default=None)
    OIPA_total_activity_count = models.IntegerField(null=True, default=None)

    def __unicode__(self):
        return self.org_id


class IatiXmlSource(models.Model):
    ref = models.CharField(
        max_length=70)
    title = models.CharField(max_length=255, default="")
    type = models.IntegerField(
        choices=(
            (1, 'Activity Files'),
            (2, 'Organisation Files'),
        ),
        default=1)
    publisher = models.ForeignKey(Publisher)
    source_url = models.URLField(
        max_length=255,
        unique=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now_add=True, editable=False)
    update_interval = models.CharField(
        max_length=20,
        choices=(
            ('day', 'Day'),
            ('week', 'Week'),
            ('month', 'Month'),
            ('year', 'Year'),
        ),
        default="month")
    last_found_in_registry = models.DateTimeField(default=None, null=True)
    xml_activity_count = models.IntegerField(null=True, default=None)
    oipa_activity_count = models.IntegerField(null=True, default=None)
    iati_standard_version = models.CharField(max_length=10, default="")
    is_parsed = models.BooleanField(null=False, default=False)
    added_manually = models.BooleanField(null=False, default=True)
    last_hash = models.CharField(max_length=32, default="")

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["ref"]

    def __unicode__(self):
        return self.ref

    def get_parse_status(self):
        return mark_safe("<a data-xml='xml_%i' class='parse-btn'>Parse</a>") % self.id
    get_parse_status.allow_tags = True
    get_parse_status.short_description = _(u"Parse status")

    def get_parse_activity(self):
        return mark_safe("<input type='text' name='activity-id' placeholder='activity id'></input><a data-xml='xml_%i' class='parse-activity-btn'>Parse Activity</a>") % self.id
    get_parse_activity.allow_tags = True
    get_parse_activity.short_description = _(u"Parse Activity")


    def process(self):
        parser = ParseIATI(self)
        parser.parse_all()

        self.is_parsed = True
        self.date_updated = datetime.datetime.now()

        self.save(process=False)

        # activity_counter = ParseAdmin()
        # self.xml_activity_count = activity_counter.get_xml_activity_amount(self.source_url)
        # self.oipa_activity_count = activity_counter.get_oipa_activity_amount(self.ref)

    def process_activity(self, activity_id):
        """
        process a single activity
        """
        parser = ParseIATI(self)
        parser.parse_activity(activity_id)

    def save(self, process=False , added_manually=True, *args, **kwargs):
        self.added_manually = added_manually
        super(IatiXmlSource, self).save()

        if process:
            self.process()

    def delete(self, *args, **kwargs):
        from iati.models import Activity
        Activity.objects.filter(xml_source_ref=self.ref).delete()
        super(IatiXmlSource, self).delete()


class Codelist(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    count = models.CharField(max_length=10, blank=True, null=True)
    fields = models.CharField(max_length=255, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self,):
        return "%s" % self.name

