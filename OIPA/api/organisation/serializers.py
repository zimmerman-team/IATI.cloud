from rest_framework import serializers
import iati


class OrganisationDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='organisation-detail')

    class Meta:
        model = iati.models.Organisation
        fields = ()


class OrganisationListSerializer(OrganisationDetailSerializer):
    class Meta:
        model = iati.models.Organisation
        fields = ('url', 'code', 'name',)
