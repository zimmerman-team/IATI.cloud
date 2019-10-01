from django.db import models


class ActivityDelete(models.Model):
    activity_id = models.IntegerField(default=0)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True
    )
