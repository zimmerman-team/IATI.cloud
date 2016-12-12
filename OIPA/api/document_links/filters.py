from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import OneToOneRel

from django_filters import FilterSet
from django_filters import NumberFilter
from django_filters import DateFilter
from django_filters import BooleanFilter
from django_filters import TypedChoiceFilter

from distutils.util import strtobool

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import TogetherFilterSet
from api.generics.filters import ToManyFilter

from rest_framework import filters
from iati.models import *

class DocumentFilter(TogetherFilterSet):
    class Meta:
        model = Document
        #together_exclusive = [('budget_period_start', 'budget_period_end')]
