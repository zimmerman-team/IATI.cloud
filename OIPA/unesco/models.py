from decimal import Decimal
from django.db import models

from iati.models import Activity, Currency, Sector


class TransactionBalance(models.Model):
    # TODO: make a test
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

    def __str__(self):
        return "Activity: %s - last update: %s" % (
            self.activity.iati_identifier, self.updated_at)


class SectorBudgetBalance(models.Model):
    # TODO: make a test
    updated_at = models.DateTimeField(auto_now=True)
    transaction_balance = models.ForeignKey(
        TransactionBalance, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    total_budget = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0))

    def __str__(self):
        return 'Activity: {iati_identifier} - sector: {sector} last update: {updated_at}'.format(  # NOQA: E501
            iati_identifier=self.transaction_balance.activity.iati_identifier,
            sector=self.sector,
            updated_at=self.updated_at
        )
