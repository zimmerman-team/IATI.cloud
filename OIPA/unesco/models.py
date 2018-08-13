from decimal import Decimal
from django.db import models

from iati.models import Activity, Currency


class TransactionBalance(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    total_budget = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0))
    total_expenditure = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0))
    cumulative_budget = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0))
    cumulative_expenditure = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0))

    def __unicode__(self, ):
        return "Activity: %s - last update: %s" % (
            self.activity.iati_identifier, self.updated_at)
