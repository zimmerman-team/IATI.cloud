from django.conf import settings
from api.publisher import serializers
from api.permissions.serializers import OrganisationUserSerializer
from iati_synchroniser.models import Publisher
from api.publisher.filters import PublisherFilter
from rest_framework.generics import RetrieveAPIView
from api.generics.views import DynamicListView, DynamicDetailView

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from common.util import get_or_none

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from api.publisher.permissions import OrganisationAdminGroupPermissions

from iati_synchroniser.models import Publisher
from iati.permissions.models import OrganisationGroup, OrganisationAdminGroup
from django.contrib.auth.models import Group, User

class PublisherList(DynamicListView):
    """
    Returns a list of IATI Publishers stored in OIPA.

    ## Request parameters

    - `publisher_iati_id` (*optional*): Publisher id to search for.
    - `org_abbreviation` (*optional*): Publisher abbreviation to search for.
    - `name` (*optional*): Filter publishers name to search for.

    ## Result details

    Each result item contains short information about the publisher including the URI
    to publisher details.

    URI is constructed as follows: `/api/publishers/{publisher_iati_id}`

    """
    queryset = Publisher.objects.all()
    serializer_class = serializers.PublisherSerializer
    filter_class = PublisherFilter

    fields = (
        'url',
        'publisher_iati_id',
        'display_name',
        'name',
        'activities')


class PublisherDetail(DynamicDetailView):
    """
    Returns detailed information about a publisher.

    ## URI Format

    ```
    /api/publishers/{publisher_iati_id}
    ```

    ### URI Parameters

    - `publisher_iati_id`: ID of the desired publisher

    """
    queryset = Publisher.objects.all()
    serializer_class = serializers.PublisherSerializer

class OrganisationAdminGroupView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def get(self, request, publisher_id):
        users = OrganisationAdminGroup.objects.get(publisher_id=publisher_id).user_set.all()

        serializer = OrganisationUserSerializer(users, many=True)

        return Response(serializer.data)

    def post(self, request, publisher_id):
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        user_id = request.data.get('user_id', None)
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        admin_group.user_set.add(user)

        return Response()

class OrganisationAdminGroupDetailView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def delete(self, request, publisher_id, id):
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        user_id = id
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        # TODO: user can remove himself from admin group? - 2016-10-24
        # if user.id == request.user.id:
        #     return Response(status=401)

        if user.id == admin_group.owner.id:
            return Response(status=401)

        admin_group.user_set.remove(user)

        return Response()



class OrganisationGroupView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def get(self, request, publisher_id):
        users = OrganisationGroup.objects.get(publisher_id=publisher_id).user_set.all()

        serializer = OrganisationUserSerializer(users, many=True)

        return Response(serializer.data)

    def post(self, request, publisher_id):
        group = OrganisationGroup.objects.get(publisher_id=publisher_id)

        user_id = request.data.get('user_id', None)
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        group.user_set.add(user)

        return Response()

class OrganisationGroupDetailView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def delete(self, request, publisher_id, id):
        publisher = Publisher.objects.get(pk=publisher_id)
        group = OrganisationGroup.objects.get(publisher_id=publisher_id)

        user_id = id
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        # TODO: user can remove himself from  group? - 2016-10-24
        # if user.id == request.user.id:
        #     return Response(status=401)

        # The user to remove is an admin
        if user.groups.filter(organisationadmingroup__publisher=publisher).exists():
            return Response(status=401)

        group.user_set.remove(user)

        return Response()

from ckanapi import RemoteCKAN, NotAuthorized

class OrganisationVerifyApiKey(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def post(self, request, publisher_id):

        # TODO: If verifying for the first time, OrganisationGroup and OrganisationAdminGroup don't exist yet. - 2016-10-25

        # publisher = Publisher.objects.get(pk=publisher_id)
        # group = OrganisationAdminGroup.objects.get(publisher_id=publisher_id)

        api_key = request.data.get('apiKey')
        user_id = request.data.get('userId')

        if not api_key or not user_id:
            return Response(status=401)

        client = RemoteCKAN(settings.CKAN_URL, apikey=api_key)

        try:
            result = client.call_action('user_show', { 
                "id": user_id,
                "include_datasets": True,
            })
        except NotAuthorized:
            return Response(status=401)

        # print('got user')
        # print(result)

        try:
            orgList = client.call_action('organization_list_for_user', {})
        except NotAuthorized:
            return Response(status=401)

        # print('got orgList')
        # print(orgList)

        if not len(orgList):
            return Response(status=401)

        primary_org_id = orgList[0]['id']

        try:
            primary_org = client.call_action('organization_show', { "id": primary_org_id })
        except NotAuthorized:
            return Response(status=401)

        if not primary_org:
            return Response(status=401)

        primary_org_iati_id = primary_org.get('publisher_iati_id')
        
        if not len(primary_org_iati_id):
            return Response(status=401)

        # TODO: add organisation foreign key - 2016-10-25
        publisher = Publisher.objects.get_or_create(
            pk=primary_org_id,
            publisher_iati_id=primary_org_iati_id,
            defaults={
                "name": primary_org.get('name'),
                "display_name": primary_org.get('display_name'),
                "image_url": primary_org.get('display_name'),
            }
        )

        print(publisher)

        # publisher = {
        #     "apiKey": api_key,
        #     "userId": user_id,
        #     "validationStatus": True,
        #     "ownerOrg": orgList.result[0].id,
        #     "datasets": 
        # }

        # TODO: now update the user - 2016-10-25


        return Response()
