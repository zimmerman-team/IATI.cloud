from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.db import models

from geodata.models import Country, Region
from iati.models import (
    BudgetStatus, Currency, DocumentCategory, FileFormat, Language,
    OrganisationType, Version
)
from iati_vocabulary.models import RegionVocabulary

from .organisation_manager import OrganisationManager


# function for making url
def make_abs_url(org_identifier):
    return '/api/organisation/' + org_identifier


# narrative for adding free text to elements
class OrganisationNarrative(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField(
        verbose_name='related object',
        db_index=True,
    )
    related_object = GenericForeignKey()

    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = models.TextField()

    def __unicode__(self,):
        return "%s" % self.content[:30]

    class Meta:
        index_together = [('content_type', 'object_id')]


class BudgetLineAbstract(models.Model):
    ref = models.CharField(max_length=150)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True,
                                default=None)
    value_date = models.DateField(null=True)
    narratives = GenericRelation(OrganisationNarrative)

    class Meta:
        abstract = True

# organisation base class


class Organisation(models.Model):
    """
    This model is initially filled by the IATI Registry API.
    Then updated by content of the IATI organisation file if available.
    Or created by an activity file if the organisation is not the publisher
    and thereby not initially filled.
    """

    organisation_identifier = models.CharField(
        max_length=150, unique=True, db_index=True)
    # normalized for use in the API, should be deprecated and fixed by a
    # proper regex in the URL - 2017-11-06
    normalized_organisation_identifier = models.CharField(
        max_length=150, db_index=True)

    iati_standard_version = models.ForeignKey(Version,
                                              on_delete=models.CASCADE)
    last_updated_datetime = models.DateTimeField(blank=True, null=True)

    default_currency = models.ForeignKey(Currency, null=True,
                                         on_delete=models.CASCADE)
    default_lang = models.ForeignKey(Language, null=True,
                                     on_delete=models.CASCADE)

    # 'iati_synchroniser.Dataset' is used to avoid circular imports
    dataset = models.ForeignKey('iati_synchroniser.Dataset', null=True,
                                default=None,
                                on_delete=models.CASCADE)
    reported_in_iati = models.BooleanField(default=True)

    # this is actually reported on activity/reporting-org but we store it here
    # so we can simultaneously update it for all activities
    type = models.ForeignKey(OrganisationType, null=True, default=None,
                             blank=True, on_delete=models.CASCADE)
    # first narrative
    primary_name = models.CharField(max_length=150, db_index=True)

    # is this organisation published to the IATI registry?
    published = models.BooleanField(default=False, db_index=True)
    # is this organisation marked as being published in the next export?
    ready_to_publish = models.BooleanField(default=False, db_index=True)
    # is this organisation changed from the originally parsed version?
    modified = models.BooleanField(default=False, db_index=True)

    objects = OrganisationManager()

    class Meta:
        ordering = ['organisation_identifier']

    def __unicode__(self):
        return self.organisation_identifier


# class for narrative
class OrganisationName(models.Model):
    organisation = models.OneToOneField(Organisation, related_name="name",
                                        on_delete=models.CASCADE)
    narratives = GenericRelation(OrganisationNarrative)


class OrganisationReportingOrganisation(models.Model):
    organisation = models.OneToOneField(
        Organisation, related_name='reporting_org', on_delete=models.CASCADE)
    org_type = models.ForeignKey(OrganisationType, null=True, default=None,
                                 on_delete=models.CASCADE)
    reporting_org = models.ForeignKey(
        Organisation,
        related_name='reported_by_orgs',
        null=True,
        db_constraint=False, on_delete=models.CASCADE)
    reporting_org_identifier = models.CharField(max_length=250, null=True)
    secondary_reporter = models.BooleanField(default=False)

    narratives = GenericRelation(OrganisationNarrative)


class TotalBudget(models.Model):
    organisation = models.ForeignKey(
        Organisation, related_name="total_budgets", on_delete=models.CASCADE)
    status = models.ForeignKey(BudgetStatus, default=1,
                               on_delete=models.CASCADE)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)


class TotalBudgetLine(BudgetLineAbstract):
    total_budget = models.ForeignKey(TotalBudget, on_delete=models.CASCADE)


class RecipientOrgBudget(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    status = models.ForeignKey(BudgetStatus, default=1,
                               on_delete=models.CASCADE)
    recipient_org_identifier = models.CharField(
        max_length=150, verbose_name='recipient_org_identifier', null=True)
    recipient_org = models.ForeignKey(
        Organisation, related_name='recieving_org', null=True,
        on_delete=models.CASCADE)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    narratives = GenericRelation(OrganisationNarrative)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)


class RecipientOrgBudgetLine(BudgetLineAbstract):
    recipient_org_budget = models.ForeignKey(RecipientOrgBudget,
                                             on_delete=models.CASCADE)


class RecipientCountryBudget(models.Model):
    organisation = models.ForeignKey(
        Organisation, related_name='recipient_country_budgets',
        on_delete=models.CASCADE)
    status = models.ForeignKey(BudgetStatus, default=1,
                               on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)


class RecipientCountryBudgetLine(BudgetLineAbstract):
    recipient_country_budget = models.ForeignKey(
        RecipientCountryBudget, on_delete=models.CASCADE)


class RecipientRegionBudget(models.Model):
    organisation = models.ForeignKey(
        Organisation, related_name='recipient_region_budget',
        on_delete=models.CASCADE)
    status = models.ForeignKey(
        BudgetStatus, default=1, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, null=True, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(RegionVocabulary, default=1,
                                   on_delete=models.CASCADE)
    vocabulary_uri = models.URLField(null=True, blank=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)


class RecipientRegionBudgetLine(BudgetLineAbstract):
    recipient_region_budget = models.ForeignKey(RecipientRegionBudget,
                                                on_delete=models.CASCADE)


class TotalExpenditure(models.Model):
    organisation = models.ForeignKey(
        Organisation, related_name="total_expenditure",
        on_delete=models.CASCADE)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    value_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)
    narratives = GenericRelation(OrganisationNarrative)


class TotalExpenditureLine(models.Model):
    total_expenditure = models.ForeignKey(
        TotalExpenditure, on_delete=models.CASCADE)

    ref = models.CharField(max_length=150)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, default=None)
    value_date = models.DateField(null=True)
    narratives = GenericRelation(OrganisationNarrative)


class OrganisationDocumentLink(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, default=None,
                                    on_delete=models.CASCADE)

    categories = models.ManyToManyField(
        DocumentCategory,
        through="OrganisationDocumentLinkCategory")

    language = models.ForeignKey(Language, null=True, default=None,
                                 on_delete=models.CASCADE)

    recipient_countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name='recipient_countries',
        through="DocumentLinkRecipientCountry"
    )

    iso_date = models.DateField(null=True, blank=True)

    def __unicode__(self,):
        return "%s - %s" % (
            self.organisation.organisation_identifier, self.url
        )

    def get_absolute_url(self):
        return make_abs_url(self.organisation.organisation_identifier)

# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this


class OrganisationDocumentLinkCategory(models.Model):
    document_link = models.ForeignKey(OrganisationDocumentLink,
                                      on_delete=models.CASCADE)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Document link categories"

# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this


class DocumentLinkRecipientCountry(models.Model):
    document_link = models.ForeignKey(OrganisationDocumentLink,
                                      on_delete=models.CASCADE)
    recipient_country = models.ForeignKey(Country, on_delete=models.CASCADE)

    narratives = GenericRelation(OrganisationNarrative)

    class Meta:
        verbose_name_plural = "Document link categories"


class DocumentLinkTitle(models.Model):
    document_link = models.OneToOneField(OrganisationDocumentLink,
                                         on_delete=models.CASCADE)
    narratives = GenericRelation(OrganisationNarrative)


class OrganisationDocumentLinkLanguage(models.Model):
    document_link = models.ForeignKey(
        OrganisationDocumentLink, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, null=True, blank=True, default=None,
                                 on_delete=models.CASCADE)


class DocumentLinkDescription(models.Model):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/document-link/description/
    """
    document_link = models.OneToOneField(
        OrganisationDocumentLink,
        on_delete=models.CASCADE
    )
    narratives = GenericRelation(OrganisationNarrative)
