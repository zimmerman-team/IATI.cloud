import os
from api.dataset.serializers import DatasetSerializer, SimpleDatasetSerializer, DatasetNoteSerializer, \
    SimplePublisherSerializer
from iati_synchroniser.models import Dataset, Publisher, DatasetNote
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from api.dataset.filters import DatasetFilter, NoteFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from django.db.models import Sum, Count
from api.generics.views import DynamicListView, DynamicDetailView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from iati.models import Activity

from rest_framework.views import APIView
from rest_framework import authentication, permissions

from iati.permissions.models import OrganisationGroup, OrganisationAdminGroup
from api.publisher.permissions import OrganisationAdminGroupPermissions

from rest_framework import exceptions

from iati_synchroniser.admin import export_xml_by_source

from django.db.models import Q
from datetime import datetime

from django.conf import settings
from rest_framework import pagination

from django.http import HttpResponse


class DatasetPagination(pagination.PageNumberPagination):
    max_page_size = 10000
    page_size = 10
    page_size_query_param = 'page_size'


class DatasetList(CacheResponseMixin, DynamicListView):
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
    pagination_class = DatasetPagination

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
        'note_count',
        'added_manually',
    )


class DatasetDetail(CacheResponseMixin, RetrieveAPIView):
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

    filter_backends = (DjangoFilterBackend,)
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
            fields=(
                "datasetnote__message",
                "datasetnote__field",
                "datasetnote__model",
                "datasetnote__exception_type"),
            renamed_fields=("message", "field", "model", "exception_type"),
        ),
    )


class DatasetNotes(CacheResponseMixin, ListAPIView):
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
    filter_class = NoteFilter

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return DatasetNote.objects.filter(dataset=pk).order_by('id')


from api.export.views import IATIActivityList

export_view = IATIActivityList.as_view()

from ckanapi import RemoteCKAN, NotAuthorized, NotFound


class DatasetPublishActivities(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions,)

    def post(self, request, publisher_id):
        user = request.user.organisationuser
        iati_user_id = user.iati_user_id
        publisher = Publisher.objects.get(pk=publisher_id)
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        source_url = request.data.get('source_url', None)

        if not source_url:
            raise exceptions.APIException(detail="no source_url provided")

        user = request.user
        organisationuser = user.organisationuser
        api_key = organisationuser.iati_api_key
        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        # TODO: should this be the name? - 2017-02-20
        source_name = '{}-activities'.format(publisher.name)

        # get all published activities, except for the ones that are just modified
        activities = Activity.objects.filter(ready_to_publish=True, publisher=publisher)

        try:
            orgList = client.call_action('organization_list_for_user', {})
        except BaseException:
            raise exceptions.APIException(
                detail="Can't get organisation list for user".format(user_id))

        primary_org_id = orgList[0]['id']

        try:
            # sync main datasets to IATI registry
            registry_dataset = client.call_action('package_create', {
                "resources": [
                    {"url": source_url}
                ],
                "name": source_name,
                "filetype": "activity",
                "date_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "activity_count": activities.count(),
                "title": source_name,
                "owner_org": primary_org_id,
                "url": source_url,
            })

        except Exception as e:
            # try to recover from case when the dataset already exists (just update it instead)

            old_package = client.call_action('package_show', {
                "name_or_id": source_name,
            })

            if not old_package:
                print('exception raised in client_call_action', e, e.error_dict)
                raise exceptions.APIException(detail="Failed publishing dataset")

            registry_dataset = client.call_action('package_update', {
                "id": old_package.get('id'),
                "resources": [
                    {"url": source_url}
                ],
                "name": source_name,
                "filetype": "activity",
                "date_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "activity_count": activities.count(),
                "title": source_name,
                "owner_org": primary_org_id,
                "url": source_url,
            })

            # over here change the iati_id so we have no uniqueness conflict
            Dataset.objects.filter(
                iati_id=old_package.get('id')).update(
                iati_id=old_package.get('id') +
                        "will_be_removed")

        # 0. create_or_update Dataset object
        dataset = Dataset.objects.get(
            filetype=1,
            publisher=publisher,
            added_manually=True,
        )

        dataset.iati_id = registry_dataset['id']
        dataset.name = source_name
        dataset.title = source_name
        dataset.source_url = source_url
        dataset.is_parsed = False
        dataset.save()

        #  update the affected activities flags
        activities.update(published=True, modified=False, ready_to_publish=True, dataset=dataset)
        Dataset.objects.filter(iati_id=old_package.get('id') + "will_be_removed").delete()

        # remove the old datasets from the registry
        # TODO: query the registry to remove a dataset - 2017-01-16
        # TODO: remove old datasets locally as well - 2017-01-16
        # TODO: Or just ask the user to remove the old datasets by hand? - 2017-02-20

        # return Dataset object
        serializer = DatasetSerializer(dataset, context={'request': request})
        return Response(serializer.data)


class DatasetPublishActivitiesUpdate(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions,)

    def put(self, request, publisher_id, dataset_id):
        user = request.user.organisationuser
        publisher = Publisher.objects.get(pk=publisher_id)
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        source_url = request.data.get('source_url', None)

        # TODO: call package_update to update source_url for registry as well - 2017-02-20

        if not source_url:
            raise exceptions.APIException(detail="no source_url provided")

        user = request.user
        organisationuser = user.organisationuser
        api_key = organisationuser.iati_api_key
        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        dataset = Dataset.objects.get(id=dataset_id)
        dataset.date_updated = datetime.now()
        dataset.source_url = source_url
        dataset.save()

        # get all ready to publish activities
        activities = Activity.objects.filter(ready_to_publish=True, publisher=publisher)
        non_r2p_activities = Activity.objects.filter(ready_to_publish=False, publisher=publisher)

        #  update the affected activities flags
        activities.update(
            published=True,
            modified=False,
            ready_to_publish=True,
            last_updated_datetime=datetime.now().isoformat(' ')
        )
        non_r2p_activities.update(published=False)

        #  return Dataset object
        serializer = DatasetSerializer(dataset, context={'request': request})
        return Response(serializer.data)


class DatasetPublishOrganisations(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions,)

    def post(self, request, publisher_id):
        user = request.user.organisationuser
        iati_user_id = user.iati_user_id
        publisher = Publisher.objects.get(pk=publisher_id)
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        source_url = request.data.get('source_url', None)

        if not source_url:
            raise exceptions.APIException(detail="no source_url provided")

        user = request.user
        organisationuser = user.organisationuser
        api_key = organisationuser.iati_api_key
        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        # TODO: should this be the name? - 2017-02-20
        source_name = '{}-organisations'.format(publisher.name)

        # get all published organisations, except for the ones that are just modified
        organisations = Organisation.objects.filter(ready_to_publish=True, publisher=publisher)

        try:
            orgList = client.call_action('organization_list_for_user', {})
        except BaseException:
            raise exceptions.APIException(
                detail="Can't get organisation list for user".format(user_id))

        primary_org_id = orgList[0]['id']

        try:
            # sync main datasets to IATI registry
            registry_dataset = client.call_action('package_create', {
                "resources": [
                    {"url": source_url}
                ],
                "name": source_name,
                "filetype": "organisation",
                "date_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "organisation_count": organisations.count(),
                "title": source_name,
                "owner_org": primary_org_id,
                "url": source_url,
            })

        except Exception as e:
            # try to recover from case when the dataset already exists (just update it instead)

            old_package = client.call_action('package_show', {
                "name_or_id": source_name,
            })

            if not old_package:
                print('exception raised in client_call_action', e, e.error_dict)
                raise exceptions.APIException(detail="Failed publishing dataset")

            registry_dataset = client.call_action('package_update', {
                "id": old_package.get('id'),
                "resources": [
                    {"url": source_url}
                ],
                "name": source_name,
                "filetype": "organisation",
                "date_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "organisation_count": organisations.count(),
                "title": source_name,
                "owner_org": primary_org_id,
                "url": source_url,
            })

        # 0. create_or_update Dataset object
        dataset = Dataset.objects.get(
            filetype=2,
            publisher=publisher,
            added_manually=True,
        )

        dataset.iati_id = registry_dataset['id']
        dataset.name = source_name
        dataset.title = source_name
        dataset.source_url = source_url
        dataset.is_parsed = False
        dataset.save()

        #  update the affected organisations flags
        organisations.update(published=True, modified=False, ready_to_publish=True)

        # remove the old datasets from the registry
        # TODO: query the registry to remove a dataset - 2017-01-16
        # TODO: remove old datasets locally as well - 2017-01-16
        # TODO: Or just ask the user to remove the old datasets by hand? - 2017-02-20

        # return Dataset object
        serializer = DatasetSerializer(dataset, context={'request': request})
        return Response(serializer.data)


class DatasetPublishOrganisationsUpdate(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions,)

    def put(self, request, publisher_id, dataset_id):
        user = request.user.organisationuser
        publisher = Publisher.objects.get(pk=publisher_id)
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        source_url = request.data.get('source_url', None)

        # TODO: call package_update to update source_url for registry as well - 2017-02-20

        if not source_url:
            raise exceptions.APIException(detail="no source_url provided")

        user = request.user
        organisationuser = user.organisationuser
        api_key = organisationuser.iati_api_key
        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        dataset = Dataset.objects.get(id=dataset_id)
        dataset.date_updated = datetime.now()
        dataset.source_url = source_url
        dataset.save()

        # get all ready to publish organisations
        organisations = Organisation.objects.filter(ready_to_publish=True, publisher=publisher)
        non_r2p_organisations = Organisation.objects.filter(
            ready_to_publish=False, publisher=publisher)

        #  update the affected organisations flags
        organisations.update(
            published=True,
            modified=False,
            ready_to_publish=True,
            last_updated_datetime=datetime.now().isoformat(' ')
        )
        non_r2p_organisations.update(published=False)

        #  return Dataset object
        serializer = DatasetSerializer(dataset, context={'request': request})
        return Response(serializer.data)


def staging_collection(request):
    path = settings.IATI_STAGING_PATH
    file = settings.IATI_STAGING_FILE_ID
    return HttpResponse(open(os.path.join(path, file)).read(), content_type='text/xml')
