from django.db import models
from iati_vocabulary.models import RegionVocabulary, GeographicVocabulary, PolicyMarkerVocabulary, SectorVocabulary, BudgetIdentifierVocabulary


class Language(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ActivityDateType(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s" % self.name


class ActivityStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class AidTypeCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class AidType(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(AidTypeCategory, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=1)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class CollaborationType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ConditionType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s" % self.name


class Currency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = "Currencies"


class DescriptionType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DisbursementChannel(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.TextField(default="")
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DocumentCategoryCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DocumentCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(DocumentCategoryCategory,
                                 on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name = "Document category"
        verbose_name_plural = "Document categories"


class FileFormat(models.Model):
    code = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.CharField(max_length=100, default="")

    def __unicode__(self,):
        return self.name


class FinanceTypeCategory(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FinanceType(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=220)
    description = models.TextField(default="")
    category = models.ForeignKey(FinanceTypeCategory, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FlowType(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GazetteerAgency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicalPrecision(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicLocationClass(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicLocationReach(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicExactness(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class HumanitarianScopeType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LocationTypeCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LocationType(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(LocationTypeCategory,
                                 on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

# renamed but unused in 201 (renamed to IATIOrganisationIdentifier)


class OrganisationIdentifier(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    abbreviation = models.CharField(max_length=30, default=None, null=True)
    name = models.CharField(max_length=200, default=None, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationRole(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class PolicyMarker(models.Model):
    code = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    vocabulary = models.ForeignKey(PolicyMarkerVocabulary, null=True,
                                   default=None, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s" % self.name


class PolicySignificance(models.Model):
    code = models.CharField(primary_key=True, max_length=1)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class PublisherType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class RelatedActivityType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ResultType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class SectorCategory(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Sector(models.Model):
    code = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(SectorCategory, null=True, default=None,
                                 on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(SectorVocabulary, null=True, default=None,
                                   on_delete=models.CASCADE)
    # check why percentage is here, looks like an error - 2016-07-22
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class TiedStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

# deprecated in 201


class ValueType(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class VerificationStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ActivityScope(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

# deprecated in 201


class AidTypeFlag(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifierSectorCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifierSector(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(BudgetIdentifierSectorCategory,
                                 on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifier(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.ForeignKey(BudgetIdentifierSector,
                                 on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(BudgetIdentifierVocabulary, null=True,
                                   default=None, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ContactType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LoanRepaymentPeriod(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LoanRepaymentType(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Version(models.Model):
    code = models.CharField(primary_key=True, max_length=4, default="")
    name = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    url = models.URLField()

    def __unicode__(self,):
        return self.code


class OtherIdentifierType(models.Model):
    code = models.CharField(primary_key=True, max_length=3, default="")
    name = models.CharField(max_length=200, default="")
    description = models.TextField(default="")

    def __unicode__(self,):
        return self.name


class IndicatorMeasure(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationRegistrationAgency(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    category = models.CharField(max_length=2)
    url = models.URLField(default="")
    public_database = models.BooleanField(default=False)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


# Deliberately not named like the codelist CrsAddOtherFlags
# since this would conflict with the M2M rel CrsAddOtherFlags
class OtherFlags(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class CRSChannelCode(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class TransactionType(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __unicode__(self,):
        return "%s" % self.name
