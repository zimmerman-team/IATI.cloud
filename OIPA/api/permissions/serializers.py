from rest_framework import serializers
from django.contrib.auth.models import Group
from iati.permissions.models import OrganisationUser, OrganisationAdminGroup, OrganisationGroup
from api.publisher.serializers import PublisherSerializer

class OrganisationUserSerializer(serializers.ModelSerializer):

    admin_groups = serializers.SerializerMethodField()
    organisation_groups = serializers.SerializerMethodField()
    is_validated = serializers.SerializerMethodField()

    def get_admin_groups(self, user):
        qs = OrganisationAdminGroup.objects.filter(user=user)
        serializer = OrganisationAdminGroupSerializer(instance=qs, many=True)
        return serializer.data

    def get_organisation_groups(self, user):
        qs = OrganisationGroup.objects.filter(user=user)
        serializer = OrganisationGroupSerializer(instance=qs, many=True)
        return serializer.data

    def get_is_validated(self, user):
        return bool(user.iati_api_key)

    class Meta:
        model = OrganisationUser
        fields = ('username', 'email', 'organisation_groups', 'admin_groups', 'is_validated')

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

