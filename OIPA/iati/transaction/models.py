from django.db import models


class TransactionType(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=40)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Transaction(models.Model):
    activity = models.ForeignKey('Activity')
    aid_type = models.ForeignKey('AidType', null=True, default=None)
    description = models.TextField(null=True, default=None)
    description_type = models.ForeignKey(
        'DescriptionType',
        null=True,
        default=None)
    disbursement_channel = models.ForeignKey(
        'DisbursementChannel',
        null=True,
        default=None)
    finance_type = models.ForeignKey('FinanceType', null=True, default=None)
    flow_type = models.ForeignKey('FlowType', null=True, default=None)
    provider_organisation = models.ForeignKey(
        'Organisation',
        related_name="transaction_providing_organisation",
        null=True,
        default=None)
    provider_organisation_name = models.CharField(
        max_length=255,
        null=True,
        default=None)
    provider_activity = models.CharField(max_length=100, null=True)
    receiver_organisation = models.ForeignKey(
        'Organisation',
        related_name="transaction_receiving_organisation",
        null=True,
        default=None)
    receiver_organisation_name = models.CharField(
        max_length=255,
        null=True,
        default=None)
    tied_status = models.ForeignKey('TiedStatus', null=True, default=None)
    transaction_date = models.DateField(null=True, default=None)
    transaction_type = models.ForeignKey(
        TransactionType,
        null=True,
        default=None)
    value_date = models.DateField(null=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey('Currency', null=True, default=None)
    ref = models.CharField(max_length=255, null=True, default=None)

    def __unicode__(self,):
        return "%s: %s - %s" % (self.activity,
                                self.transaction_type,
                                self.transaction_date)
