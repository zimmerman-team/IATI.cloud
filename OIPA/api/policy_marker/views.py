import iati
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
import serializers

class PolicyMarkerList(ListAPIView):
    """
    Returns a list of IATI Policy markers stored in OIPA.

    ## Request parameters

    - `code` (*optional*): Country code to search for.
    - `name` (*optional*): Country name to search for.
    - `region_code` (*optional*): Filter countries by Region code.
    - `fields` (*optional*): List of fields to display.
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Available aggregations

    API request may include `fields[aggregations]` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in countries activities list.
    - `disbursement`: Calculate total disbursement of activities
        presented in countries activities list.
    - `commitment`: Calculate total commitment of activities
        presented in countries activities list.

    ## Result details

    Each result item contains short information about country including URI
    to country details.

    URI is constructed as follows: `/api/counties/{country_id}`

    """
    queryset = iati.models.PolicyMarker.objects.all()
    serializer_class = serializers.PolicyMarkerSerializer
    fields = ('code','name', 'description','vocabulary','policy_marker_related')

