from django.db import models
from geodata.models import Country


class UnescoIndicator(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    description = models.TextField(null=True, blank=True)
    friendly_label = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.id

class UnescoIndicatorData(models.Model):
    unesco_indicator = models.ForeignKey(UnescoIndicator)
    country = models.ForeignKey(Country, null=True)
    value = models.FloatField(null=True, blank=True)
    type_value = models.IntegerField(blank=True, null=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Unesco indicator data"

    def __unicode__(self):
        return self.unesco_indicator.id
