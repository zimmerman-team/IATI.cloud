import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        fixtures = [
            'test_vocabulary',
            'test_codelists.json',
            'test_geodata.json'
        ]

        for fixture in fixtures:
            call_command("loaddata", fixture)
