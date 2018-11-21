from django.core.management.base import BaseCommand

from iati.document_search_indexes import (
    reindex_all_documents, reindex_document
)
from iati.models import Document


class Command(BaseCommand):
    """
        Reindex full text search values for all documents
    """

    def add_arguments(self, document_collector):
        document_collector.add_argument('--document',
                                        action='store',
                                        dest='document',
                                        default=None,
                                        help='Reindex only this document')

    def handle(self, *args, **options):
        if options['document']:
            document = Document.objects.get(document_link=options['document'])
            reindex_document(document)
        else:
            reindex_all_documents()
