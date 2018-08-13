from django.db.models import signals
from django.dispatch import receiver

from . import models
from unesco.cron import calculated_transaction_balance_for_one_activity


@receiver(signals.post_save, sender=models.Transaction)
def transaction_post_save(sender, instance, **kwargs):
    calculated_transaction_balance_for_one_activity(instance.activity)
