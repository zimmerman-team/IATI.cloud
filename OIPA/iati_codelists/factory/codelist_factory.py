import iati 
from iati_codelists import models as codelist_models

from factory import SubFactory, RelatedFactory
from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0

class GetOrCreateMetaMixin():
    django_get_or_create = ('code',)

class VersionFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.Version
        django_get_or_create = ('code',)

    code = '2.01'
    name = 'IATI version 2.01'

class LanguageFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.Language
        django_get_or_create = ('code',)

    code = 'en'
    name = 'english'

class FileFormatFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.FileFormat

    code = 'application/json'
    name = ''

class DocumentCategoryCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.DocumentCategoryCategory

    code = 'A'
    name = 'Activity Level'

class DocumentCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.DocumentCategory

    code = 'A04'
    name = 'Conditions'
    category = SubFactory(DocumentCategoryCategoryFactory)


class BudgetTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.BudgetType

    code = '1'
    name = 'Original'


class BudgetStatusFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.BudgetStatus

    code = '1'
    name = 'Indicative'


class ActivityDateTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.ActivityDateType

    code = '1'
    name = 'Planned start'

class CurrencyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.Currency

    code = 'USD'
    name = 'us dolar'


class CollaborationTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.CollaborationType

    code = 1
    name = 'Bilateral'


class ActivityStatusFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.ActivityStatus

    code = "1"
    name = 'Pipeline/identification'


class FlowTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.FlowType

    code = 1
    name = 'test-flowtype'
    description = 'test-flowtype-description'


class AidTypeCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.AidTypeCategory

    code = 1
    name = 'test-category'
    description = 'test-category-description'


class AidTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.AidType

    code = 1
    name = 'test'
    description = 'test'
    category = SubFactory(AidTypeCategoryFactory)


class DescriptionTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.DescriptionType

    code = "1"
    name = 'General'
    description = 'description here'


class ContactTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.ContactType

    code = "1"
    name = 'General Enquiries'
    description = 'General Enquiries'


class SectorFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.Sector

    code = 200
    name = 'advice'
    description = ''


class SectorCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.SectorCategory

    code = 200
    name = 'education'
    description = 'education description'


class OrganisationTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.OrganisationType

    code = '10'
    name = 'Government'


class OrganisationRoleFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.OrganisationRole

    code = '1'
    name = 'Funding'


class BudgetIdentifierSectorCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.BudgetIdentifierSectorCategory

    code = "1"
    name = "General Public Service"


class BudgetIdentifierSectorFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.BudgetIdentifierSector

    code = "1.1"
    name = "Executive"
    category = SubFactory(BudgetIdentifierSectorCategoryFactory)

class BudgetIdentifierFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.BudgetIdentifier

    code = "1"
    name = "IATI"
    category = SubFactory(BudgetIdentifierSectorFactory)


class PolicyMarkerFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.PolicyMarker

    code = "1"
    name = 'Gender Equality'


class PolicySignificanceFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.PolicySignificance

    code = "0"
    name = 'not targeted'
    description = 'test description'


class FinanceTypeCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.FinanceTypeCategory

    code = "100"
    name = "GRANT"

class FinanceTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.FinanceType

    code = "110"
    name = 'Aid grant excluding debt reorganisation'
    category = SubFactory(FinanceTypeCategoryFactory)


class TiedStatusFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.TiedStatus

    code = "3"
    name = 'Partially tied'


class ResultTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.ResultType

    code = "2"
    name = 'ResultType'

class GeographicLocationClassFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.GeographicLocationClass

    code = "2"
    name = 'Populated place'


class GeographicLocationReachFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.GeographicLocationReach

    code = "1"
    name = 'Activity'


class GeographicExactnessFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.GeographicExactness

    code = "1"
    name = 'Exact'


class LocationTypeCategoryFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.LocationTypeCategory

    code = 'S'
    name = 'Spot Features'


class LocationTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.LocationType

    code = 'AIRQ'
    name = 'abandoned airfield'
    description = 'abandoned airfield'
    category = LocationTypeCategoryFactory.build()


class ActivityScopeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.ActivityScope

    code = "1"
    name = 'example scope'


class HumanitarianScopeTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.HumanitarianScopeType

    code = "1"
    name = 'Emergency'

from iati.transaction.models import TransactionType

class TransactionTypeFactory(NoDatabaseFactory):
    code = "1"
    name = "Incoming Funds"
    description = ""

    class Meta:
        model = TransactionType

class DisbursementChannelFactory(NoDatabaseFactory):
    code = "1"
    name = "Money is disbursed through central Ministry of Finance or Treasury"
    description = ""

    class Meta:
        model = codelist_models.DisbursementChannel

class IndicatorMeasureFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.IndicatorMeasure

    code = "1"
    name = "Unit"

class OtherIdentifierTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.OtherIdentifierType

    code = 'A1'
    name = 'Reporting Organisations internal activity identifier'


class ConditionTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.ConditionType

    code = '1'
    name = 'Policy'

class LoanRepaymentTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.LoanRepaymentType

    code = '1'
    name = 'Equal Principal Payments'

class LoanRepaymentPeriodFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.LoanRepaymentPeriod

    code = '1'
    name = 'Annual'

class OtherFlagsFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.OtherFlags

    code = '1'

class RelatedActivityTypeFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = iati.models.RelatedActivityType

    code = '1'
    name = 'Parent'
