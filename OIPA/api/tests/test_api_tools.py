from django.test import TestCase
import pytest
from api.api_tools import comma_separated_parameter_to_list

@pytest.mark.parametrize("input,expected", [
    ('descriptions,titles,identifiers', ['descriptions', 'titles', 'identifiers']), #should work when the param contains no whitespace
    ('descriptions, titles, identifiers', ['descriptions', 'titles', 'identifiers']), #should work when the param contains whitespace after ','
    ('    descriptions    ,    titles    ,   identifiers'   , ['descriptions', 'titles', 'identifiers']), #should work when the param contains unexpected whitespace
])
def test_comma_separated_parameter_to_list(input, expected):
    assert comma_separated_parameter_to_list(input) == expected