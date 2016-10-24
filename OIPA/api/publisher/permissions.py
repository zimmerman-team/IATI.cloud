from rest_framework import permissions

from common.util import get_or_none

from iati_synchroniser.models import Publisher
from iati.permissions.models import OrganisationGroup, OrganisationAdminGroup

class OrganisationAdminGroupPermissions(permissions.BasePermission):
    message = 'You have no admin priviledges for this organisation'

    def has_permission(self, request, view):
        """
        Check if the user is in
        """

        # TODO: this might be dangerous - 2016-10-24
        if request.method == 'GET':
            return True

        user = request.user

        if not request.user or not request.user.is_authenticated:
            return False

        publisher_id = view.kwargs.get('pk')
        
        try:
            publisher = Publisher.objects.get(pk=publisher_id)
        except Publisher.DoesNotExist:
            return False

        try:
            admin_group = OrganisationAdminGroup.objects.get(publisher=publisher)
        except OrganisationAdminGroup.DoesNotExist:
            return False

        return user.groups.filter(organisationadmingroup__publisher=publisher).exists()

