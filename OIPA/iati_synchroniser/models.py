from django.db import models
import datetime
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from iati_organisation.models import Organisation


class Publisher(models.Model):

    # The IR publisher id
    id = models.CharField(max_length=255, primary_key=True)

    # the IATI Organisation id
    publisher_iati_id = models.CharField(max_length=100)

    # name given in the IR API
    name = models.CharField(max_length=55, default="")
    display_name = models.CharField(max_length=255)

    organisation = models.OneToOneField(Organisation, default=None, null=True)

    def __unicode__(self):
        return self.publisher_iati_id

filetype_choices = (
    (1, 'Activity'),
    (2, 'Organisation'),
)

class Dataset(models.Model):
    
    # IR fields
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default="")
    filetype = models.IntegerField(choices=filetype_choices, default=1)
    publisher = models.ForeignKey(Publisher) # organization.id
    source_url = models.URLField(max_length=255) # resource.url
    iati_version = models.CharField(max_length=10, default="")
    
    # OIPA related fields
    date_created = models.DateTimeField(default=datetime.datetime.now, editable=False)
    date_updated = models.DateTimeField(default=datetime.datetime.now, editable=False)
    time_to_parse = models.CharField(null=True, default=None, max_length=40)
    last_found_in_registry = models.DateTimeField(default=None, null=True)
    is_parsed = models.BooleanField(null=False, default=False)
    added_manually = models.BooleanField(null=False, default=True)
    sha1 = models.CharField(max_length=40, default="", null=False, blank=True)
    note_count = models.IntegerField(default=0)

    export_in_progress = models.BooleanField(default=False)
    parse_in_progress = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["name"]

    def __unicode__(self):
        return self.name

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

    def save(self, process=False, *args, **kwargs):
        super(Dataset, self).save()

        if process:
            self.process()


class DatasetNote(models.Model):
    dataset = models.ForeignKey(Dataset)
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
    date_updated = models.DateTimeField(default=datetime.datetime.now, editable=False)

    def __unicode__(self,):
        return "%s" % self.name

