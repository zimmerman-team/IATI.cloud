from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import DjangoFilterBackend

from api.document_links import serializers as documentSerializers
from api.document_links import filters
from api.generics.filters import SearchFilter
from api.generics.views import DynamicListView


from iati.models import Document



class DocumentList(DynamicListView):
    """
    Returns a list of IATI DocumentLinks stored in OIPA.

    ## Text search

    API request may include `q` parameter. This parameter controls text search
    and contains expected value.

    By default, searching is performed on `document_content` the document content

    By default, search only return results if the hit resembles a full word. 
    This can be altered through the `q_lookup` parameter. Options for this parameter are:

    - `exact` (default): Only return results when the query hit is a full word.
    - `startswith`: Also returns results when the word stars with the query. 


    """

    queryset = Document.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = filters.DocumentFilter
    serializer_class = documentSerializers.DocumentSerializer

    fields = (
        'id',
        'document_name',
        'long_url',
        #'document_content',
        'document_link')

    always_ordering = 'id'

    ordering_fields = (
        'document_name')

