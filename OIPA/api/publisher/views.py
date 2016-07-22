from api.publisher import serializers
from iati_synchroniser.models import Publisher
from api.publisher.filters import PublisherFilter
from rest_framework.generics import RetrieveAPIView
from api.generics.views import DynamicListView, DynamicDetailView


class PublisherList(DynamicListView):
    """
    Returns a list of IATI Publishers stored in OIPA.

    ## Request parameters

    - `org_id` (*optional*): Publisher id to search for.
    - `org_abbreviation` (*optional*): Publisher abbreviation to search for.
    - `org_name` (*optional*): Filter publishers name to search for.

    ## Result details

    Each result item contains short information about the publisher including the URI
    to publisher details.

    URI is constructed as follows: `/api/publishers/{org_id}`

    """
    queryset = Publisher.objects.all()
    serializer_class = serializers.PublisherSerializer
    filter_class = PublisherFilter

    fields = (
        'url',
        'org_id',
        'org_abbreviate',
        'org_name',
        'activities')


class PublisherDetail(DynamicDetailView):
    """
    Returns detailed information about a publisher.

    ## URI Format

    ```
    /api/publishers/{org_id}
    ```

    ### URI Parameters

    - `org_id`: ID of the desired publisher

    """
    queryset = Publisher.objects.all()
    serializer_class = serializers.PublisherSerializer

