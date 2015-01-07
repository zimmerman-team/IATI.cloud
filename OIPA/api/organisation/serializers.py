import django.utils.http
import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsModelSerializer


class OrganisationSerializer(DynamicFieldsModelSerializer):
    class EncodedHyperlinkedIdentityField(
            serializers.HyperlinkedIdentityField):
        def get_url(self, obj, view_name, request, format):
            if obj.pk is None:
                return None
            lookup_value = getattr(obj, self.lookup_field)
            quoted_lookup_value = django.utils.http.urlquote(lookup_value)

            kwargs = {self.lookup_url_kwarg: quoted_lookup_value}
            return self.reverse(
                view_name, kwargs=kwargs, request=request, format=format)

    url = EncodedHyperlinkedIdentityField(view_name='organisation-detail')

    class Meta:
        model = iati.models.Organisation
        fields = (
            'url',
            'code',
            'abbreviation',
            'type',
            'reported_by_organisation',
            'name',
            'original_ref',

            # Reverse linked data
            'activity_reporting_organisation',
            'activity_set',
            'activityparticipatingorganisation_set',
            'transaction_providing_organisation',
            'transaction_receiving_organisation',
        )
