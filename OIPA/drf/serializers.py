from django.contrib.auth.models import User, Group
from iati.models import  Activity, Description, Title
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ActivitySerializer(serializers.HyperlinkedModelSerializer):
	description_set = serializers.RelatedField(many=True)
	title_set = serializers.RelatedField(many=True)
	class Meta:
		model = Activity
		fields = ('id', 'description_set', 'title_set')