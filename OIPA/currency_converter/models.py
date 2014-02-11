from django.db import models
from iati.models import Transaction
from currency_converter.converter import CurrencyConverter

class Converter(models.Model):
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = "Currency converter"

    def __unicode__(self,):
        return "%s" % (self.call)

class ToConvertList(models.Model):
    transaction = models.ForeignKey(Transaction)
    added_on = models.DateTimeField(auto_now=True)

    def __unicode__(self,):
        return "%s" % (self.transaction)
