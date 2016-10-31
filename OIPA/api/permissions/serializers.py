from rest_framework import serializers
from django.contrib.auth.models import Group
from iati.permissions.models import OrganisationUser

class OrganisationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganisationUser
        fields = ('username', 'email',)

