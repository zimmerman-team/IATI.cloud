from django.db import models
from django.test import TestCase
from unittest import skip


class Model(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=160)


class TestFilter(TestCase):
    @skip('filter test')
    def test_incorrect_lookup(self):
        pass

    @skip('filter test')
    def test_unknown_model_filter(self):
        pass

    @skip('filter test')
    def test_unknown_field(self):
        pass

    @skip('filter test')
    def test_valid_filter(self):
        pass
