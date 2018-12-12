from django.db.models import signals
from django.dispatch import receiver

from iati.models import ActivitySector
from iom.models import ProjectType


@receiver(signals.post_save, sender=ActivitySector)
def activity_sector_post_save(sender, instance, **kwargs):
    if instance.vocabulary.code == '99':
        try:
            ProjectType.objects.get(
                activity=instance.activity, sector=instance.sector)
        except ProjectType.DoesNotExist:
            ProjectType(
                activity=instance.activity, sector=instance.sector).save()
