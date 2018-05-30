from django.contrib.auth.models import User
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from api.generics.serializers import DynamicFieldsModelSerializer
from api.publisher.serializers import PublisherSerializer
from iati.permissions.models import (
    OrganisationAdminGroup, OrganisationGroup, OrganisationUser
)


class OrganisationGroupSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()

    class Meta:
        model = OrganisationGroup
        fields = ('name', 'publisher')


class OrganisationAdminGroupSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()

    class Meta:
        model = OrganisationAdminGroup
        fields = ('name', 'publisher',)


class UserSerializer(DynamicFieldsModelSerializer):

    username = serializers.CharField()
    email = serializers.EmailField()

    admin_groups = serializers.SerializerMethodField()
    organisation_groups = serializers.SerializerMethodField()

    is_validated = serializers.SerializerMethodField()

    admin_groups = OrganisationAdminGroupSerializer(
        many=True, source="organisationuser.organisation_admin_groups")
    organisation_groups = OrganisationGroupSerializer(
        many=True, source="organisationuser.organisation_groups")

    def get_is_validated(self, user):
        try:
            return bool(user.organisationuser.iati_api_key)
        except OrganisationUser.DoesNotExist:
            return False

    class Meta:
        model = User
        fields = ('username', 'email', 'organisation_groups',
                  'admin_groups', 'is_validated')


class OrganisationUserSerializer(DynamicFieldsModelSerializer):

    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    admin_groups = serializers.SerializerMethodField()
    organisation_groups = serializers.SerializerMethodField()
    is_validated = serializers.SerializerMethodField()

    admin_groups = OrganisationAdminGroupSerializer(
        many=True, source="organisation_admin_groups")
    organisation_groups = OrganisationAdminGroupSerializer(many=True)

    def get_is_validated(self, user):
        return bool(user.iati_api_key)

    class Meta:
        model = OrganisationUser
        fields = ('username', 'email', 'organisation_groups',
                  'admin_groups', 'is_validated')


class RegistrationSerializer(RegisterSerializer):

    def custom_signup(self, request, user):
        OrganisationUser.objects.create(user=user)
