from api.dataset.serializers import DatasetSerializer
from iati_synchroniser.models import IatiXmlSource
from rest_framework.generics import RetrieveAPIView
from api.dataset.filters import DatasetFilter

from api.generics.views import DynamicListView, DynamicDetailView

class DatasetList(DynamicListView):
    """
    Returns a list of IATI datasets stored in OIPA.

    ## Request parameters

    - `ref` (*optional*): ref to search for.
    - `type` (*optional*): Filter datasets by type (activity or organisation).
    - `publisher` (*optional*): List of publisher refs.


    ## Result details

    Each result item contains full information about datasets including URI
    to dataset details.

    URI is constructed as follows: `/api/datasets/{ref}`

    """
    queryset = IatiXmlSource.objects.all()
    serializer_class = DatasetSerializer
    filter_class = DatasetFilter

    fields = (
        'ref',
        'title',
        'type',
        'publisher',
        'url',
        'source_url',
        'activities',
        'activity_count',
        'date_created',
        'date_updated',
        'last_found_in_registry',
        'iati_standard_version')


class DatasetDetail(RetrieveAPIView):
    """
    Returns detailed information about the dataset.

    ## URI Format

    ```
    /api/datasets/{ref}
    ```

    """
    queryset = IatiXmlSource.objects.all()
    serializer_class = DatasetSerializer

    fields = (
        'ref',
        'title',
        'type',
        'publisher',
        'url',
        'activities',
        'activity_count',
        'date_created',
        'date_updated',
        'last_found_in_registry',
        'iati_standard_version')