from api.generics.filters import BasicFilter
from api.generics.filters import BasicFilterBackend
from api.generics.filters import FilterField
from django.db import models
from unittest import TestCase


class TestModel(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=160)


class TestFilter(TestCase):
    def test_incorrect_lookup(self):
        self.assertRaises(
            AssertionError, FilterField, lookup_type='i', field='code')

    def test_unknown_model_filter(self):
        class UnknownModelFieldFilter(BasicFilter):
            codes = FilterField(lookup_type='in', field='unknown_field')

            class Meta:
                model = TestModel
                fields = [
                    'codes'
                ]

        self.assertRaises(AssertionError, UnknownModelFieldFilter)

    def test_unknown_field(self):
        class UnknownFieldFilter(BasicFilter):
            codes = FilterField(lookup_type='in', field='code')

            class Meta:
                model = TestModel
                fields = [
                    'codes',
                    'name'
                ]

        self.assertRaises(AssertionError, UnknownFieldFilter)

    def test_valid_filter(self):
        class CorrectFilter(BasicFilter):
            codes = FilterField(lookup_type='in', field='code')
            name = FilterField(lookup_type='icontains', field='name')

            class Meta:
                model = TestModel
                fields = [
                    'codes',
                    'name'
                ]

        params = {
            'codes': '1,3',
            'name': 'test'
        }
        expected_result = {
            'code__in': ['1', '3'],
            'name__icontains': 'test'
        }
        result = BasicFilterBackend().filter_field_queryset_parameters(
            params=params,
            filter=CorrectFilter
        )
        assert result == expected_result
