import os
from django.db import models
from django.utils.text import slugify
from geodata.models import Country, City, Region
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class IndicatorTopic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    source_note = models.TextField(null=True)

class LendingType(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)

class IncomeLevel(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)

class IndicatorSource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()

class Indicator(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    description = models.TextField(null=True, blank=True)
    friendly_label = models.CharField(max_length=255, null=True, blank=True)
    type_data = models.CharField(max_length=255, null=True, blank=True)
    #selection type is used for i.e. table 14 type of fuel this attribute is removed to IndicatorData (31-03-2014)
    #selection_type = models.CharField(max_length=255, null=True, blank=True)

    #deprivation type is used for i.e. table 14 urban, non slum household, one sheltar deprivation
    deprivation_type = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey(IndicatorSource, null=True, blank=True)
    topic = models.ForeignKey(IndicatorTopic, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return self.friendly_label

class IndicatorData(models.Model):
    indicator = models.ForeignKey(Indicator)
    country = models.ForeignKey(Country, null=True)
    city = models.ForeignKey(City, null=True)
    region = models.ForeignKey(Region, null=True)
    value = models.DecimalField(null=True, blank=True, db_index=True, max_digits=17, decimal_places=4)
    year = models.IntegerField(max_length=5)
    selection_type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "indicator data"

    def __unicode__(self):
        return self.indicator.friendly_label

def file_upload_to(instance, filename):
    path = settings.ADMINFILES_UPLOAD_TO
    try:
        name, ext = filename.rsplit('.', 1)
    except ValueError:
        # when file has no extension
        name = filename
        ext = None
    name = slugify(name).replace('-','_')
    return os.path.join(path, '%s%s%s' % (name, ext and '.' or '',
        ext or ''))

class CsvUploadLog(models.Model):
    upload_date = models.DateTimeField(_('Upload date'), auto_now_add=True)
    upload = models.FileField(_('File'), upload_to=file_upload_to,
        blank=True, null=True, max_length=255)
    title = models.CharField(_('title'), max_length=100, null=True, blank=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    link = models.URLField(_('link'), max_length=500, null=True, blank=True)
    description = models.CharField(_('description'), blank=True, max_length=200)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=_(u'uploaded by'), related_name='uploaded_files')
    cities_not_found = models.TextField(null=True, blank=True)
    countries_not_found = models.TextField(null=True, blank=True)
    total_countries_found = models.IntegerField(null=True, blank=True)
    total_countries_not_found = models.IntegerField(null=True, blank=True)
    total_cities_not_found = models.IntegerField(null=True, blank=True)
    total_cities_found = models.IntegerField(null=True, blank=True)
    total_items_saved = models.IntegerField(null=True, blank=True)
