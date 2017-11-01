from django.db import models
import datetime
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class Publisher(models.Model):
    org_id = models.CharField(max_length=100)
    org_abbreviate = models.CharField(max_length=55, default="")
    org_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.org_id


class IatiXmlSource(models.Model):
    ref = models.CharField(
        max_length=255)
    title = models.CharField(max_length=255, default="")
    type = models.IntegerField(
        choices=(
            (1, 'Activity'),
            (2, 'Organisation'),
        ),
        default=1)
    publisher = models.ForeignKey(Publisher)
    source_url = models.URLField(
        max_length=255,
        unique=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now_add=True, editable=False)
    time_to_parse = models.CharField(null=True, default=None, max_length=40)
    last_found_in_registry = models.DateTimeField(default=None, null=True)
    iati_standard_version = models.CharField(max_length=10, default="")
    is_parsed = models.BooleanField(null=False, default=False)
    added_manually = models.BooleanField(null=False, default=True)
    sha1 = models.CharField(max_length=40, default="", null=False, blank=True)
    note_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["ref"]

    def __unicode__(self):
        return self.ref

    def get_parse_status(self):
        return mark_safe("<a data-xml='xml_%i' class='admin-btn parse-btn'>Add to parser queue</a>") % self.id
    get_parse_status.allow_tags = True
    get_parse_status.short_description = _(u"Parse")

    def get_parse_activity(self):
        return mark_safe("<input type='text' name='activity-id' placeholder='activity id'><a data-xml='xml_%i' class='admin-btn parse-activity-btn'>Parse Activity</a>") % self.id
    get_parse_activity.allow_tags = True
    get_parse_activity.short_description = _(u"Parse Activity")

    def process(self, force_reparse=False):
        from iati.parser.parse_manager import ParseManager
        start_datetime = datetime.datetime.now()
        
        parser = ParseManager(self, force_reparse=force_reparse)
        parser.parse_all()
        self.is_parsed = True
        
        self.date_updated = datetime.datetime.now()

        time_diff = self.date_updated - start_datetime
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        def prepend_zero(time_period):
            if time_period < 10:
                return '0' + str(time_period)
            return time_period

        self.time_to_parse = '%s:%s:%s' % (prepend_zero(hours), prepend_zero(minutes), prepend_zero(seconds))

        self.save(process=False)

    def process_activity(self, activity_id):
        """
        process a single activity
        """
        from iati.parser.parse_manager import ParseManager
        parser = ParseManager(self)
        parser.parse_activity(activity_id)

    def save(self, process=False, added_manually=True, *args, **kwargs):
        self.added_manually = added_manually
        super(IatiXmlSource, self).save()

        if process:
            self.process()


class IatiXmlSourceNote(models.Model):
    source = models.ForeignKey(IatiXmlSource)
    iati_identifier = models.CharField(max_length=140, null=False, blank=False)
    exception_type = models.CharField(max_length=100, blank=False, null=False)
    model = models.CharField(max_length=50, null=False, blank=False)
    field = models.CharField(max_length=100, default='')
    message = models.CharField(max_length=150, default=0, null=False)
    line_number = models.IntegerField(null=True)


class Codelist(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    count = models.CharField(max_length=10, blank=True, null=True)
    fields = models.CharField(max_length=255, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self,):
        return "%s" % self.name

