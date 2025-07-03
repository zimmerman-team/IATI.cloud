from django.db import models


class Currency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name_plural = "Currencies"


class MonthlyAverage(models.Model):

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    imf_url = models.URLField(max_length=2000, null=True)
    value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True,
        default=None)

    class Meta:
        unique_together = ("currency", "month", "year")

    def __unicode__(self,):
        return f"{self.currency_id}: {self.year}-{self.month}"
