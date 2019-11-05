from api.country.serializers import CountrySerializer
from api.organisation import serializers


class OrganisationRecipientRegionBudgetSerializer(
    serializers.OrganisationRecipientRegionBudgetSerializer
):
    recipient_region = serializers.BasicRegionSerializer(
        source="region", fields=('code', 'name', 'region_vocabulary'))


class OrganisationRecipientCountryBudgetSerializer(
    serializers.OrganisationRecipientCountryBudgetSerializer
):
    recipient_country = CountrySerializer(
        source="country", fields=('code', 'name'))
