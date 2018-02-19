from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from iati.models import OrganisationType
from iati.models import Language
from iati.models import Currency
from iati.models import FileFormat
from iati.models import DocumentCategory
from iati.models import Version
from iati.models import BudgetStatus
from geodata.models import Country
from geodata.models import Region
from iati_vocabulary.models import RegionVocabulary

from iati_codelists.models import *
from iati_vocabulary.models import *

from organisation_manager import OrganisationManager

#function for making url
def make_abs_url(org_identifier):
    return '/api/organisation/'+org_identifier

#narrative for adding free text to elements
class OrganisationNarrative(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(
        verbose_name='related object',
        db_index=True,
    )
    related_object = GenericForeignKey()

    organisation = models.ForeignKey('Organisation')

    language = models.ForeignKey(Language)
    content = models.TextField()

    def __unicode__(self,):
        return "%s" % self.content[:30]

    class Meta:
        index_together = [('content_type', 'object_id')]

class BudgetLineAbstract(models.Model):
    ref = models.CharField(max_length=150)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    value_date = models.DateField(null=True)
    narratives = GenericRelation(OrganisationNarrative)

    class Meta:
        abstract = True

# organisation base class
class Organisation(models.Model):
    """
    This model is initially filled by the IATI Registry API.
    Then updated by content of the IATI organisation file if available.
    Or created by an activity file if the organisation is not the publisher and thereby not initially filled.
    """

    organisation_identifier = models.CharField(max_length=150, unique=True, db_index=True)
    # normalized for use in the API, should be deprecated and fixed by a proper regex in the URL - 2017-11-06
    normalized_organisation_identifier = models.CharField(max_length=150, db_index=True)

    iati_standard_version = models.ForeignKey(Version)
    last_updated_datetime = models.DateTimeField(blank=True, null=True)

    default_currency = models.ForeignKey(Currency, null=True)
    default_lang = models.ForeignKey(Language, null=True)

    reported_in_iati = models.BooleanField(default=True)

    # this is actually reported on activity/reporting-org but we store it here so we can simultaneously update it for all activities
    type = models.ForeignKey(OrganisationType, null=True, default=None, blank=True)

    # first narrative
    primary_name = models.CharField(max_length=150, db_index=True)

    # is this organisation published to the IATI registry?
    published = models.BooleanField(default=False, db_index=True)
    # is this organisation marked as being published in the next export?
    ready_to_publish = models.BooleanField(default=False, db_index=True)
    # is this organisation changed from the originally parsed version?
    modified = models.BooleanField(default=False, db_index=True)

    objects = OrganisationManager()

    def __unicode__(self):
        return self.organisation_identifier


#class for narrative
class OrganisationName(models.Model):
    organisation = models.OneToOneField(Organisation, related_name="name")
    narratives = GenericRelation(OrganisationNarrative)


class OrganisationReportingOrganisation(models.Model):
    organisation = models.OneToOneField(Organisation, related_name='reporting_org')
    org_type = models.ForeignKey(OrganisationType, null=True, default=None)
    reporting_org = models.ForeignKey(Organisation,related_name='reported_by_orgs',null=True, db_constraint=False)
    reporting_org_identifier = models.CharField(max_length=250,null=True)
    secondary_reporter = models.BooleanField(default=False)

    narratives = GenericRelation(OrganisationNarrative)


class TotalBudget(models.Model):
    organisation = models.ForeignKey(Organisation,related_name="total_budgets")
    status = models.ForeignKey(BudgetStatus, default=1)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)

class TotalBudgetLine(BudgetLineAbstract):
    total_budget = models.ForeignKey(TotalBudget)

class RecipientOrgBudget(models.Model):
    organisation = models.ForeignKey(Organisation)
    status = models.ForeignKey(BudgetStatus, default=1)
    recipient_org_identifier = models.CharField(max_length=150, verbose_name='recipient_org_identifier', null=True)
    recipient_org = models.ForeignKey(Organisation, related_name='recieving_org', null=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    narratives = GenericRelation(OrganisationNarrative)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)

class RecipientOrgBudgetLine(BudgetLineAbstract):
    recipient_org_budget = models.ForeignKey(RecipientOrgBudget)

class RecipientCountryBudget(models.Model):
    organisation = models.ForeignKey(Organisation,related_name='recipient_country_budgets')
    status = models.ForeignKey(BudgetStatus, default=1)
    country = models.ForeignKey(Country, null=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)

class RecipientCountryBudgetLine(BudgetLineAbstract):
    recipient_country_budget = models.ForeignKey(RecipientCountryBudget)

class RecipientRegionBudget(models.Model):
    organisation = models.ForeignKey(Organisation, related_name='recipient_region_budget')
    status = models.ForeignKey(BudgetStatus, default=1)
    region = models.ForeignKey(Region, null=True)
    vocabulary = models.ForeignKey(RegionVocabulary, default=1)
    vocabulary_uri = models.URLField(null=True, blank=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)

class RecipientRegionBudgetLine(BudgetLineAbstract):
    recipient_region_budget = models.ForeignKey(RecipientRegionBudget)

class TotalExpenditure(models.Model):
    organisation = models.ForeignKey(Organisation,related_name="total_expenditure")
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)

class TotalExpenditureLine(models.Model):
    total_expenditure = models.ForeignKey(TotalExpenditure)

    ref = models.CharField(max_length=150)
    currency = models.ForeignKey(Currency,null=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=None)
    value_date = models.DateField(null=True)
    narratives = GenericRelation(OrganisationNarrative)

class OrganisationDocumentLink(models.Model):
    organisation = models.ForeignKey(Organisation)
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, default=None)

    categories = models.ManyToManyField(
        DocumentCategory,
        through="OrganisationDocumentLinkCategory")

    language = models.ForeignKey(Language, null=True, default=None)

    recipient_countries = models.ManyToManyField(
        Country, 
        blank=True,
        related_name='recipient_countries',
        through="DocumentLinkRecipientCountry"
        )

    iso_date = models.DateField(null=True, blank=True)

    def __unicode__(self,):
        return "%s - %s" % (self.organisation.organisation_identifier, self.url)

    def get_absolute_url(self):
        return make_abs_url(self.organisation.organisation_identifier)

# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this
class OrganisationDocumentLinkCategory(models.Model):
    document_link = models.ForeignKey(OrganisationDocumentLink)
    category = models.ForeignKey(DocumentCategory)

    class Meta:
        verbose_name_plural = "Document link categories"

# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this
class DocumentLinkRecipientCountry(models.Model):
    document_link = models.ForeignKey(OrganisationDocumentLink)
    recipient_country = models.ForeignKey(Country)

    narratives = GenericRelation(OrganisationNarrative)

    class Meta:
        verbose_name_plural = "Document link categories"

class DocumentLinkTitle(models.Model):
    document_link = models.OneToOneField(OrganisationDocumentLink)
    narratives = GenericRelation(OrganisationNarrative)

class OrganisationDocumentLinkLanguage(models.Model):
    document_link = models.ForeignKey(OrganisationDocumentLink)
    language = models.ForeignKey(Language, null=True, blank=True, default=None)

