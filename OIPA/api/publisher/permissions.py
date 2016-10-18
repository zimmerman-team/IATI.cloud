from rest_framework import permissions

from common.util import get_or_none

from iati_synchroniser.models import Publisher
from iati.permissions.models import AdminGroup

class AdminGroupPermissions(permissions.BasePermission):
    message = 'Adding customers not allowed.'

    def has_permission(self, request, view):
        """
        Check if the user is in
        """
        user = request.user

        if not request.user or not request.user.is_authenticated:
            return False

        publisher_id = view.kwargs.get('pk')
        
        try:
            publisher = Publisher.objects.get(pk=publisher_id)
        except Publisher.DoesNotExist:
            return False

        try:
            admin_group = AdminGroup.objects.get(publisher=publisher)
        except AdminGroup.DoesNotExist:
            return False

        return user.groups.filter(admingroup__publisher=publisher).exists()

