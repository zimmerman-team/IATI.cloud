from rest_framework import authentication
from rest_framework.generics import ListAPIView
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.export_organisation import serializers as export_serializers
from api.pagination import IatiXMLPagination
from api.publisher.permissions import PublisherPermissions
from api.renderers import OrganisationXMLRenderer
from iati.models import Organisation
from iati_synchroniser.models import Publisher


class OrganisationList(CacheResponseMixin, ListAPIView):
    """
    Returns a list of IATI Organisations stored in OIPA.

    ## Result details

    Each result item contains short information about organisation
    including URI to city details.

    URI is constructed as follows: `/api/organisations/{organisation_id}`

    """
    queryset = Organisation.objects.all()

    serializer_class = export_serializers.OrganisationXMLSerializer
    pagination_class = IatiXMLPagination

    renderer_classes = (BrowsableAPIRenderer, OrganisationXMLRenderer)


class OrganisationNextExportList(ListAPIView):
    """IATI representation for organisations"""

    queryset = Organisation.objects.all()

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    serializer_class = export_serializers.OrganisationXMLSerializer
    pagination_class = IatiXMLPagination
    renderer_classes = (OrganisationXMLRenderer, )

    def get_queryset(self):
        publisher_id = self.kwargs.get('publisher_id')
        publisher = Publisher.objects.get(pk=publisher_id)

        return super(OrganisationNextExportList, self).get_queryset().filter(
            publisher=publisher).prefetch_all()
