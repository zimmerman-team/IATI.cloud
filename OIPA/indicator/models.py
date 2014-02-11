from django.db import models
from geodata.models import Country, City, Region

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
    id = models.CharField(max_length=50, primary_key=True)
    description = models.TextField(null=True, blank=True)
    friendly_label = models.CharField(max_length=255, null=True, blank=True)
    type_data = models.CharField(max_length=255, null=True, blank=True)
    # parent = models.ForeignKey()
    #selection type is used for i.e. table 14 type of fuel
    selection_type = models.CharField(max_length=255, null=True, blank=True)
    #deprivation type is used for i.e. table 14 urban, non slum household, one sheltar deprivation
    deprivation_type = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey(IndicatorSource, null=True, blank=True)
    topic = models.ForeignKey(IndicatorTopic, null=True, blank=True)

    def __unicode__(self):
        return self.friendly_label

class IndicatorData(models.Model):
    indicator = models.ForeignKey(Indicator)
    country = models.ForeignKey(Country, null=True)
    city = models.ForeignKey(City, null=True)
    region = models.ForeignKey(Region, null=True)
    value = models.FloatField(null=True, blank=True)
    year = models.IntegerField(max_length=5)

    class Meta:
        verbose_name_plural = "indicator data"
