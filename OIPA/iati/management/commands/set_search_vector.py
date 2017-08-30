from django.core.management.base import BaseCommand
from iati.models import ActivitySearch
from django.contrib.postgres.search import SearchVector


class Command(BaseCommand):

    def handle(self, *args, **options):
        ActivitySearch.objects.update(search_vector_text=SearchVector('text', config='english'))
