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

class OrganisationAdminGroupView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def get(self, request, pk):
        users = OrganisationAdminGroup.objects.get(publisher_id=pk).user_set.all()

        serializer = OrganisationUserSerializer(users, many=True)

        return Response(serializer.data)

    def post(self, request, pk):
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=pk)

        user_id = request.data.get('user_id', None)
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        admin_group.user_set.add(user)

        return Response()

class OrganisationAdminGroupDetailView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def delete(self, request, pk, id):
        admin_group = OrganisationAdminGroup.objects.get(publisher_id=pk)

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

    def get(self, request, pk):
        users = OrganisationGroup.objects.get(publisher_id=pk).user_set.all()

        serializer = OrganisationUserSerializer(users, many=True)

        return Response(serializer.data)

    def post(self, request, pk):
        group = OrganisationGroup.objects.get(publisher_id=pk)

        user_id = request.data.get('user_id', None)
        user = get_or_none(User, pk=user_id)

        if not user:
            return Response(status=401)

        group.user_set.add(user)

        return Response()

class OrganisationGroupDetailView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (OrganisationAdminGroupPermissions, )

    def delete(self, request, pk, id):
        publisher = Publisher.objects.get(pk=pk)
        group = OrganisationGroup.objects.get(publisher_id=pk)

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
