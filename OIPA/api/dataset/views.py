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

from iati.permissions.models import OrganisationGroup, OrganisationAdminGroup
from api.publisher.permissions import OrganisationAdminGroupPermissions

from rest_framework import exceptions

from iati_synchroniser.admin import export_xml_by_source

from django.db.models import Q
from datetime import datetime

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
        'id',
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

from ckanapi import RemoteCKAN, NotAuthorized, NotFound

class DatasetPublishActivities(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def post(self, request, publisher_id):
        print('called post...')
        user = request.user.organisationuser
        publisher = Publisher.objects.get(pk=publisher_id)
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        source_url = request.data.get('source_url', None)

        if not source_url:
            raise exceptions.APIException(detail="no source_url provided")

        user = request.user
        organisationuser = user.organisationuser
        api_key = organisationuser.iati_api_key
        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        source_name = '{}-activity'.format(publisher.name)

        # 0. create_or_update Dataset object
        dataset = Dataset.objects.get_or_create(
            name=source_name,
            title=source_name,
            filetype=1,
            publisher=publisher,
            source_url=source_url, # TODO: store in OIPA somewhere, or let user define this? - 2017-01-13
            is_parsed=False,
            iati_version="2.02",
                )

        # 1. actually generate the XML
        xml = export_xml_by_source(dataset.id)

        # 2. get all published activities, except for the ones that are just modified
        activities = Activity.objects.filter(
                Q(published=True) & ~(Q(ready_to_publish=False) & Q(modified=True)), publisher=publisher)

        # 3. sync main datasets to IATI registry
        try:
            dataset = client.call_action('package_create', { 
                "resources": [
                    { "url": source_url }
                ],
                "name": source_name,
                "filetype": "activity",
                "date_updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                "activity_count": activities.count(),
                "title": source_name,
                "owner_org": publisher.organisation.ref,
                "url": source_url,
            })
        except:
            raise exceptions.APIException(detail="Failed publishing dataset")

        # 5. update the affected activities flags
        activities.update(published=True, modified=False, ready_to_publish=False)

        # 6. remove the old datasets from the registry
        # TODO: query the registry to remove a dataset - 2017-01-16
        # TODO: remove old datasets locally as well - 2017-01-16

        # 7. return Dataset object
        return Response(dataset)

