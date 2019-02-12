from rest_framework import permissions

from iati.permissions.models import OrganisationAdminGroup
from iati_synchroniser.models import Publisher


class OrganisationAdminGroupPermissions(permissions.BasePermission):
    message = 'You have no admin priviledges for this organisation'

    def has_permission(self, request, view):
        """
        Check if the user is in
        """

        # TODO: this might be dangerous - 2016-10-24
        if request.method == 'GET':
            return True

        organisation_user = request.user.organisationuser
        user = request.user

        if not user or not user.is_authenticated:
            return False

        publisher_id = view.kwargs.get('publisher_id')

        try:
            publisher = Publisher.objects.get(pk=publisher_id)
        except Publisher.DoesNotExist:
            return False

        try:
            OrganisationAdminGroup.objects.get(
                publisher=publisher)
        except OrganisationAdminGroup.DoesNotExist:
            return False

        # check if this user is in the admin group

        return organisation_user.organisation_admin_groups.filter(
            publisher=publisher).exists()


class ActivityCreatePermissions(permissions.BasePermission):
    message = 'You have no admin priviledges for this publisher'

    def has_permission(self, request, view):
        """
        Check if the user is in
        """

        # TODO: this might be dangerous - 2016-10-24
        if request.method == 'GET':
            return True

        # TODO: why is this a OrganisationUser instance??? - 2016-12-19
        organisation_user = request.user.organisationuser
        user = request.user

        if not user or not user.is_authenticated:
            return False

        publisher_id = request.data.get('publisher_id')

        try:
            publisher = Publisher.objects.get(pk=publisher_id)
        except Publisher.DoesNotExist:
            return False

        try:
            OrganisationAdminGroup.objects.get(
                publisher=publisher)
        except OrganisationAdminGroup.DoesNotExist:
            return False

        # check if this user is in the admin group

        return organisation_user.organisation_admin_groups.filter(
            publisher=publisher).exists()


class PublisherPermissions(permissions.BasePermission):
    message = 'You have no admin priviledges for the publisher defined on the \
    activity'

    def has_permission(self, request, view):
        """
        Checks if the publisher_id sent along in the URL matches one of the
        OrganisationAdminGroups that the user belongs to. For Activity Update
        and Delete
        """


        return True
        # this is currently disabled. See: #1067

        """
        user = request.user
        organisation_user = user.organisationuser

        if not user or not user.is_authenticated or not organisation_user:
            return False

        publisher_id = view.kwargs.get('publisher_id')
        try:
            publisher = Publisher.objects.get(pk=publisher_id)
        except Publisher.DoesNotExist:
            return False

        try:
            OrganisationAdminGroup.objects.get(
                publisher=publisher)
        except OrganisationAdminGroup.DoesNotExist:
            return False

        # check if this user is in the admin group
        return organisation_user.organisation_admin_groups.filter(
            publisher=publisher).exists()
        """
