from django.test import TestCase
from django.test.client import RequestFactory
from django_filters import DateFilter

from api.generics.filters import TogetherFilterSet
from iati.models import Activity


class FirstFilter(TogetherFilterSet):
    budget_period_start = DateFilter(
        lookup_expr='gte',
        field_name='budget__period_start',)

    budget_period_end = DateFilter(
        lookup_expr='lte',
        field_name='budget__period_end')

    class Meta:
        model = Activity
        together_exclusive = [('budget_period_start', 'budget_period_end')]
        fields = '__all__'


class SecondFilter(TogetherFilterSet):
    budget_period_start = DateFilter(
        lookup_expr='gte',
        field_name='budget__period_start',)

    budget_period_end = DateFilter(
        lookup_expr='lte',
        field_name='budget__period_end')

    class Meta:
        model = Activity
        fields = '__all__'


class TogetherFilterSetTestCase(TestCase):

    def test_filter_is_applied_together(self):
        """
        Test when specifying together_exclusive, the filters are applied
        together
        """

        request = RequestFactory().get(
            '/api/activities/?budget_period_start=2015-04-01&budget_period_end=2016-03-31'  # NOQA: E501
        )
        query_params = request.GET

        queryset = Activity.objects.all()

        resulting_qs = FirstFilter(query_params, queryset=queryset).qs

        query = resulting_qs.query

        # only the main table and the budget table are joined
        self.assertEqual(len(query.__dict__['alias_map']), 2)

    def test_without_together_exclusive(self):
        request = RequestFactory().get(
            '/api/activities/?budget_period_start=2015-04-01&budget_period_end=2016-03-31'  # NOQA: E501
        )
        query_params = request.GET

        queryset = Activity.objects.all()

        resulting_qs = SecondFilter(query_params, queryset=queryset).qs
        query = resulting_qs.query

        # table joined twice, hence 3 aliases
        self.assertEqual(len(query.__dict__['alias_map']), 3)
