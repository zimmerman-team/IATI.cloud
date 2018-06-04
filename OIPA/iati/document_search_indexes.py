from datetime import datetime
from functools import partial

from django.core.exceptions import ObjectDoesNotExist

from common.util import print_progress, setInterval
from iati.models import Document, DocumentSearch


# TODO: prefetches - 2016-01-07
def reindex_document(document):
    try:
        document_search = DocumentSearch.objects.get(document=document.id)
    except ObjectDoesNotExist:
        document_search = DocumentSearch()

    document_search.document = document

    try:
        document_search.content = document.document_content

        document_search.text = " ".join([
            document_search.content,
        ])

        document_search.last_reindexed = datetime.now()
        document_search.save()

    # FIXME: get rid of all these prints throughout the project:
    except Exception as e:
        print("Building ft indexes for {id} raises: {e}".format(
            id=document.id, e=e.message)
        )


def reindex_all_documents():

    progress = {
        'offset': 0,
        'count': Document.objects.all().count()
    }

    setInterval(partial(print_progress, progress), 10)

    for docuement in Document.objects.all().iterator():
        reindex_document(docuement)
        progress['offset'] += 1
