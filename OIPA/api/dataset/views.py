from api.dataset.serializers import DatasetSerializer, SimpleDatasetSerializer, DatasetNoteSerializer, SimplePublisherSerializer
from iati_synchroniser.models import Dataset, Publisher
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from api.dataset.filters import DatasetFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from django.db.models import Sum, Count
from api.generics.views import DynamicListView, DynamicDetailView

from rest_framework.views import APIView
from rest_framework import authentication, permissions

from api.publisher.permissions import OrganisationAdminGroupPermissions

class DatasetList(DynamicListView):
    """
    Returns a list of IATI datasets stored in OIPA.

    ## Request parameters

    - `name` (*optional*): name to search for.
    - `source_type` (*optional*): Filter datasets by type (activity or organisation).
    - `publisher` (*optional*): Publisher ref.
    - `publisher_name` (*optional*): Publisher name.
    - `note_exception_type` (*optional*): Exact exception type name of notes.
    - `note_exception_type_contains` (*optional*): Word the exception type contains.
    - `note_model` (*optional*): Exact model content of notes.
    - `note_model_contains` (*optional*): Word the model contains.
    - `note_field` (*optional*): Exact field content of notes.
    - `note_field_contains` (*optional*): Word the field contains.
    - `note_message` (*optional*): Exact message content of notes.
    - `note_message_contains` (*optional*): Word the message contains.
    - `note_count_gte` (*optional*): Note count greater or equal.
    - `date_updated_gte` (*optional*): Last updated greater or equal, format exampe; `2016-01-01%2012:00:00`.

    ## Ordering

    API request may include `ordering` parameter. This parameter controls the order in which
    results are returned.

    Results can be ordered by all displayed fields.

    The user may also specify reverse orderings by prefixing the field name with '-', like so: `-note_count`

    ## Result details

    Each result item contains full information about datasets including URI
    to dataset details.

    URI is constructed as follows: `/api/datasets/{name}`

    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filter_class = DatasetFilter
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = '__all__'

    fields = (
        'name',
        'title',
        'filetype',
        'publisher',
        'url',
        'source_url',
        'activities',
        'activity_count',
        'date_created',
        'date_updated',
        'last_found_in_registry',
        'iati_version',
        'note_count')


class DatasetDetail(RetrieveAPIView):
    """
    Returns detailed information about the dataset.

    ## URI Format

    ```
    /api/datasets/{name}
    ```

    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    fields = (
        'name',
        'title',
        'type',
        'publisher',
        'url',
        'activities',
        'activity_count',
        'date_created',
        'date_updated',
        'last_found_in_registry',
        'iati_version',
        'note_count',
        'notes')


class DatasetAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `dataset`
    - `publisher`
    - `exception_type`
    - `field`
    - `model`
    - `message`
    

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `note_count` count the amount of notes

    ## Request parameters

    All filters available on the Dataset List, can be used on aggregations.

    """

    queryset = Dataset.objects.all()

    filter_backends = ( DjangoFilterBackend,)
    filter_class = DatasetFilter
    
    allowed_aggregations = (
        Aggregation(
            query_param='note_count',
            field='note_count',
            annotate=Count('datasetnote__id'),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="dataset",
            fields=("id"),
            renamed_fields="dataset",
            queryset=Dataset.objects.all(),
            serializer=SimpleDatasetSerializer,
            serializer_main_field='id'
        ),
        GroupBy(
            query_param="publisher",
            fields=("publisher__id"),
            renamed_fields="_publisher",
            queryset=Publisher.objects.all(),
            serializer=SimplePublisherSerializer,
            serializer_main_field='id'
        ),
        GroupBy(
            query_param="exception_type",
            fields=("datasetnote__exception_type"),
            renamed_fields="exception_type",
        ),
        GroupBy(
            query_param="field",
            fields=("datasetnote__field", "datasetnote__exception_type"),
            renamed_fields=("field", "exception_type"),
        ),
        GroupBy(
            query_param="model",
            fields=("datasetnote__field", "datasetnote__model", "datasetnote__exception_type"),
            renamed_fields=("field", "model", "exception_type"),
        ),
        GroupBy(
            query_param="message",
            fields=("datasetnote__message", "datasetnote__field", "datasetnote__model", "datasetnote__exception_type"),
            renamed_fields=("message", "field", "model", "exception_type"),
        ),
    )


class DatasetNotes(ListAPIView):
    """
    Returns a list of Dataset notes stored in OIPA.

    ## URI Format

    ```
    /api/datasets/{dataset_id}/notes
    ```
    """

    serializer_class = DatasetNoteSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = '__all__'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Dataset(pk=pk).datasetnote_set.all()

from api.export.views import IATIActivityList
export_view = IATIActivityList.as_view()

from ckanapi import RemoteCKAN

class DatasetPublish(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def post(self, request, publisher_id):
        publisher = Publisher.objects.get(pk=publisher_id)
        group = OrganisationGroup.objects.get(publisher_id=publisher_id)

        # TODO: create a dataset - 2016-10-25
        # export = export_view(request).content

        print(export)

        return Response()

