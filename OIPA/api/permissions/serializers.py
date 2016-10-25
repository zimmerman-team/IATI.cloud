from rest_framework import serializers
from django.contrib.auth.models import Group, User

class OrganisationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)

