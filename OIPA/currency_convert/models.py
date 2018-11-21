from django.db import models

from iati_codelists.models import Currency


class MonthlyAverage(models.Model):

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True,
        default=None)

    class Meta:
        unique_together = ("currency", "month", "year")

    def __unicode__(self,):
        return "%s: %s-%s" % (self.currency_id, self.year, self.month)
