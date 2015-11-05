from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from iati.models import OrganisationType,Language,Currency,FileFormat,DocumentCategory,Version
from iati.organisation_manager import OrganisationQuerySet
from geodata.models import Country


# Create your models here.

#function for making url
def make_abs_url(org_identifier):
    return '/api/organisation/'+org_identifier

#narrative for adding free text to elements
class Narrative(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        verbose_name='xml Parent',
        null=True,
        blank=True,
        related_name='narratives'
    )
    object_id = models.CharField(
        max_length=250,
        verbose_name='related object',
        null=True
    )
    parent_object = GenericForeignKey('content_type', 'object_id')
    language = models.ForeignKey(Language, null=True, default=None,related_name='narratives_for_lang')
    organisation_identifier = models.CharField(max_length=150,verbose_name='iati_identifier',null=True)
    content = models.TextField(null=True,blank=True)
    related_object = models.BooleanField(default=True)
    def get_absolute_url(self):
        return make_abs_url(self.organisation_identifier)



# organisation base class
class Organisation(models.Model):
    code = models.CharField(max_length=250,primary_key=True)
    abbreviation = models.CharField(max_length=120, default="")
    organisation_identifier = models.CharField(max_length=150,verbose_name='organisation_identifier',null=True)
    type = models.ForeignKey(OrganisationType, null=True, default=None,related_name='organisations')
    original_ref = models.CharField(max_length=120, default="")
    last_updated_datetime =  models.DateTimeField(null=True)
    iati_version = models.ForeignKey(Version)
    default_currency = models.ForeignKey(Currency,null=True)
    default_lang = models.ForeignKey(Language,null=True)

    def __unicode__(self):
        return self.code


#class for narrative
class Name(models.Model):
    organisation = models.ForeignKey(Organisation)
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )


#reporting organisation (can only be one but needs seperate class for narratives)
class ReportingOrg(models.Model):
    organisation = models.ForeignKey(Organisation,related_name='reporting_orgs')
    org_type = models.ForeignKey(OrganisationType, null=True, default=None)
    reporting_org = models.ForeignKey(Organisation,related_name='reported_by_orgs',null=True, db_constraint=False)
    reporting_org_identifier = models.CharField(max_length=250,null=True)
    secondary_reporter = models.BooleanField(default=False)

#budgetLine
class BudgetLine(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        verbose_name='xml Parent',
        null=True,
        blank=True,
    )
    object_id = models.CharField(
        max_length=250,
        verbose_name='related object',
        null=True,
    )
    parent_object = GenericForeignKey('content_type', 'object_id')
    organisation_identifier = models.CharField(max_length=150,verbose_name='iati_identifier',null=True)
    language = models.ForeignKey(Language, null=True, default=None)
    ref = models.CharField(max_length=150,primary_key=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
    value_date = models.DateField(null=True)
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )

    def get_absolute_url(self):
        return make_abs_url(self.organisation_identifier)


class TotalBudget(models.Model):
    organisation = models.ForeignKey(Organisation,related_name="total_budget")
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )
    budget_lines = GenericRelation(
        BudgetLine,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name="budget_lines")

class RecipientOrgBudget(models.Model):
    organisation = models.ForeignKey(Organisation,related_name='donor_org')
    recipient_org_identifier = models.CharField(max_length=150,verbose_name='recipient_org_identifier',null=True)
    recipient_org = models.ForeignKey(Organisation,related_name='recieving_org',db_constraint=False,null=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
    budget_lines = GenericRelation(
        BudgetLine,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name="budget_lines")

class RecipientCountryBudget(models.Model):
    organisation = models.ForeignKey(Organisation,related_name='recipient_country_budget')
    country = models.ForeignKey(Country,null=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )
    budget_lines = GenericRelation(
        BudgetLine,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name="budget_lines")

class DocumentLink(models.Model):
    organisation = models.ForeignKey(Organisation,related_name='documentlinks')
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, default=None,related_name='file_formats')
    categories = models.ManyToManyField(
        DocumentCategory,related_name='doc_categories')
    # title = models.CharField(max_length=255, default="")
    language = models.ForeignKey(Language, null=True, default=None,related_name='languages')
    recipient_countries = models.ManyToManyField(
        Country, blank=True,related_name='recipient_countries')

    def __unicode__(self,):
        return "%s - %s" % (self.organisation.code, self.url)

    def get_absolute_url(self):
        return make_abs_url(self.organisation.code)

# TODO: enforce one-to-one
class DocumentLinkTitle(models.Model):
    document_link = models.ForeignKey(DocumentLink,related_name='documentlinktitles')
    narratives = GenericRelation(
        Narrative,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='narratives'
    )











