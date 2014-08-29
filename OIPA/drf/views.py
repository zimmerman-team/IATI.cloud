from django.contrib.auth.models import User, Group
from iati.models import Activity
from rest_framework import viewsets, filters
from drf.serializers import UserSerializer, GroupSerializer, ActivitySerializer


class UserViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	queryset = User.objects.all()
	serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows groups to be viewed or edited.
	"""
	queryset = Group.objects.all()
	serializer_class = GroupSerializer

class ActivityViewSet(viewsets.ModelViewSet):
	queryset = Activity.objects.all()
	serializer_class = ActivitySerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('@search_description', '@search_title')