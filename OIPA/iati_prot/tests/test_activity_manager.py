from iati.activity_manager import ActivityQuerySet
from iati import models
import pytest

class TestActivityQuerySet:
	@pytest.mark.parametrize("input,expected", [
    	('food', '+food*'), #should return the query word with a prefix '+' and a suffix '*'
    	('food water aids', '+food* +water* +aids*'), #should also work when multiple words are used
	])
	def test___create_full_text_query(self, input, expected):
		assert ActivityQuerySet()._create_full_text_query(input) == expected


	@pytest.mark.parametrize("input,expected", [
    	({'sector__in':[1,2]}, True), #query should be distinct after using with __in filter
    	({'sector__contains':1}, False), #query should not be distinct after using without __in filter
		({'sector__in':[1,2], 'sector__contains':[1,2]}, True), #query should be distinct after using __in filter in combination with other filters
	])
	def test__distinct_if_necessary__use_in_filter(self, input, expected):
		qs = models.Activity.objects.all().filter(iati_identifier__exact=1).distinct_if_necessary(input)
		assert qs.query.distinct == expected


	@pytest.mark.parametrize("input,expected", [
    	({'sector__in':[1,2]}, True), #query should be distinct after using with __in filter
    	({'sector__contains':1}, False), #query should not be distinct after using without __in filter
		({'sector__in':[1,2], 'sector__contains':[1,2]}, True), #query should be distinct after using __in filter in combination with other filters
	])
	def test__prepare_search_filter(self, input, expected):
		query = 'food water'
		a = ActivityQuerySet()
		filter = a._prepare_search_filter(['descriptions', 'titles'], query)
		#should return a list of django filters, followed by the query used on the filter
		assert filter == [('activitysearchdata__search_description__search', a._create_full_text_query(query)), ('activitysearchdata__search_title__search', a._create_full_text_query(query))]


	def test__prepare_search_filter__wrong_field(self):
		with pytest.raises(Exception) as ex:
			'''should raise an exception when an invalid search_field (in this case 'spam') is used'''
			a = ActivityQuerySet()
			a._prepare_search_filter(['descriptions', 'spam'], 'food water')
		assert 'unsupported search_field' in str(ex.value)

	@pytest.mark.parametrize("input", [
    	([2012,2013]), #should work with a list containing multiple years
    	([2012]), #should work with a list containing 1 year
		(2012), #should work with an integer instead of a list
	])
	def test__filter_years(self, input):
		a = models.Activity.objects.all()
		a_filter = a.filter_years(input)
