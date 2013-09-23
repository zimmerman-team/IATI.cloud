from django.db import models
from geodata.models import country, city, region


class indicator_topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    source_note = models.TextField(null=True)


class lending_type(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)


class income_level(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)


class indicator_source(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()


class indicator(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    friendly_label = models.CharField(max_length=255, null=True, blank=True)
    type_data = models.CharField(max_length=255, null=True, blank=True)
    # parent = models.ForeignKey()
    #selection type is used for i.e. table 14 type of fuel
    selection_type = models.CharField(max_length=255, null=True, blank=True)
    #deprivation type is used for i.e. table 14 urban, non slum household, one sheltar deprivation
    deprivation_type = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey(null=True, blank=True)
    topic = models.ForeignKey(null=True, blank=True)

    def __unicode__(self):
        return self.friendly_label

class indicator_data(models.Model):
    indicator = models.ForeignKey(indicator)
    country = models.ForeignKey(country, null=True)
    city = models.ForeignKey(city, null=True)
    region = models.ForeignKey(region, null=True)
    value = models.FloatField(null=True, blank=True)
    year = models.IntegerField(max_length=5)

    class Meta:
        verbose_name_plural = "indicator data"
