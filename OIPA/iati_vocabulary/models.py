from django.db import models

# Create your models here.
class GeographicVocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    url = models.URLField()
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

class PolicyMarkerVocabulary(models.Model):
    code = models.CharField(max_length=10,  primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

class SectorVocabulary(models.Model):
    code = models.CharField(max_length=10,  primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    url = models.URLField()
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

class Vocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=140)
    description = models.TextField(default="")
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

class BudgetIdentifierVocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

class RegionVocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=20)
    description = models.TextField(default="")
    codelist_iati_version = models.CharField(max_length=4)
    codelist_successor = models.CharField(max_length=100, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

