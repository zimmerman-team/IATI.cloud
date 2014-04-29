from django.utils.translation import ugettext_lazy as _
from django.db import models

class TranslationModel(models.Model):
    key = models.CharField(max_length=150)
    language = models.CharField(max_length=5, null=False, blank=False)
    translation = models.CharField(max_length=255)

    def __unicode__(self):
        return self.key




