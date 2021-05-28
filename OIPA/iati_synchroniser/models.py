import datetime
import logging
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from lxml import etree

from iati.filegrabber import FileGrabber
from iati_organisation.models import Organisation

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Publisher(models.Model):

    # The IR publisher id
    iati_id = models.CharField(max_length=255, unique=True)

    # the IATI Organisation id
    publisher_iati_id = models.CharField(max_length=100)

    # name given in the IR API
    name = models.CharField(max_length=55, default="")
    display_name = models.CharField(max_length=255)
    package_count = models.CharField(max_length=10, default=None, null=True)
    organisation = models.OneToOneField(
        Organisation,
        default=None,
        null=True,
        on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.publisher_iati_id


filetype_choices = (
    (1, 'Activity'),
    (2, 'Organisation'),
)


class Dataset(models.Model):

    # IR fields
    iati_id = models.CharField(max_length=255, unique=True)

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default="")
    filetype = models.IntegerField(choices=filetype_choices, default=1)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE,
                                  null=True)

    source_url = models.TextField()  # resource.url
    # Internal URL where we are storing the file.
    # This can be blank because sometimes the URL might not be reachable.
    internal_url = models.URLField(max_length=255, blank=True)

    iati_version = models.CharField(max_length=255, default="2.02")
    # OIPA related fields
    date_created = models.DateTimeField(
        default=datetime.datetime.now, editable=False)
    date_updated = models.DateTimeField(
        default=datetime.datetime.now, editable=False)
    time_to_parse = models.CharField(null=True, default=None, max_length=40)
    last_found_in_registry = models.DateTimeField(
        default=None, blank=True, null=True)
    is_parsed = models.BooleanField(null=False, default=False)
    added_manually = models.BooleanField(null=False, default=True)
    sha1 = models.CharField(max_length=40, default="", null=False, blank=True)
    sync_sha1 = models.CharField(max_length=40, default="", null=False,
                                 blank=True)
    note_count = models.IntegerField(default=0)

    export_in_progress = models.BooleanField(default=False)
    parse_in_progress = models.BooleanField(default=False)

    activities_count_in_xml = models.IntegerField(default=0)
    activities_count_in_database = models.IntegerField(default=0)
    validation_status = JSONField(null=True, default=None)
    validation_md5 = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        verbose_name_plural = "IATI XML sources"
        ordering = ["name"]

    def __unicode__(self):
        return self.name

    def process(self, force_reparse=False):
        """if not self.iati_version:
            self.update_activities_count()"""
        if self.iati_version in ['2.01', '2.02', '2.03']:
            from iati.parser.parse_manager import ParseManager
            start_datetime = datetime.datetime.now()

            parser = ParseManager(self, force_reparse=force_reparse)
            parser.parse_all()
            self.update_activities_count()
            if self.activities_count_in_database == \
                    self.activities_count_in_xml:

                self.is_parsed = True
            else:
                self.is_parsed = False

            self.date_updated = datetime.datetime.now()

            time_diff = self.date_updated - start_datetime
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            def prepend_zero(time_period):
                if time_period < 10:
                    return '0' + str(time_period)
                return time_period

            self.time_to_parse = '%s:%s:%s' % (prepend_zero(
                hours), prepend_zero(minutes), prepend_zero(seconds))

            self.save(process=False)

    def process_activity(self, activity_id):
        """
        process a single activity
        """
        from iati.parser.parse_manager import ParseManager
        parser = ParseManager(self)
        parser.parse_activity(activity_id)

    def get_internal_url(self):
        """
        Constructs and returns internal URL for the Dataset
        """

        # Serve only the XML file is exists on the DataSet static folder
        file_path = Path(
            '{static_root}/{internal_url}'.format(
                static_root=settings.STATIC_ROOT,
                internal_url=self.internal_url
            )
        )
        if file_path.is_file():
            return settings.STATIC_URL + self.internal_url

        return None

    def update_activities_count(self):
        # This module to give us imformation the count activity in database
        # and in the XML

        try:
            # Activity count in the XML
            file_grabber = FileGrabber()
            response = file_grabber.get_the_file(self.source_url)

            # Parse to XML tree
            tree = etree.fromstring(response.content)

            # Get version from the XML
            if not self.iati_version:
                parser = etree.XMLParser(resolve_entities=False,
                                         no_network=True,
                                         huge_tree=True, encoding='utf-8')
                parser_tree = etree.parse(BytesIO(response.content), parser)
                root = parser_tree.getroot()

                # Continue parsing if version is 2.01 or above
                iati_version = root.xpath('@version')
                if len(iati_version) > 0:
                    iati_version = iati_version[0]

                self.iati_version = iati_version

            count = len(tree.findall('iati-activity'))
            self.activities_count_in_xml = count

            # Activity count in the Database
            self.activities_count_in_database = self.activity_set.all().count()

            self.save(process=False)
        except Exception as e:
            logger.error(e)

    def save(self, process=False, *args, **kwargs):
        super(Dataset, self).save()

        if process:
            self.process()


class DatasetNote(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    iati_identifier = models.CharField(max_length=255, null=False, blank=False)
    exception_type = models.CharField(max_length=100, blank=False, null=False)
    model = models.CharField(max_length=255, null=False, blank=False)
    field = models.CharField(max_length=255, default='')
    message = models.CharField(max_length=255, default='', null=False)
    line_number = models.IntegerField(null=True)
    variable = models.CharField(max_length=255, default=None, null=True)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True)


class DatasetFailedPickup(models.Model):
    """
    Specification:
    Name of publisher
    Publisher Identifier
    Publisher IATI Identifier
    Dataset Filename
    Dataset Identifier
    Timestamp
    Type of error
    """
    publisher_name = models.CharField(max_length=255, null=True, blank=False)
    publisher_identifier = models.CharField(max_length=255, null=True,
                                            blank=False)
    dataset_filename = models.CharField(max_length=255, null=True, blank=False)
    dataset_url = models.URLField(max_length=255, blank=True)
    is_http_error = models.BooleanField(null=False, default=False)
    status_code = models.CharField(max_length=100, blank=False, null=True)
    error_detail = models.TextField(max_length=1000, blank=False, null=True)
    timestamp = models.DateTimeField(
        null=False, blank=True, auto_now=True)


class DatasetUpdateDates(models.Model):
    success = models.BooleanField(null=False, default=False)
    timestamp = models.DateTimeField(
        null=False, blank=True, auto_now=False)


# This model is added for the automation of the incremental parsing procedure
class DatasetDownloadsStarted(models.Model):
    timestamp = models.DateTimeField(
        null=False, blank=True, auto_now=True)


# This model is added for the automation of the incremental parsing procedure
class AsyncTasksFinished(models.Model):
    timestamp = models.DateTimeField(
        null=False, blank=True, auto_now=True)


class Codelist(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    count = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Count of different codes in this codelist',
    )
    fields = models.CharField(max_length=255, blank=True, null=True)
    date_updated = models.DateTimeField(
        default=datetime.datetime.now, editable=False)

    def __unicode__(self,):
        return "%s" % self.name
