from api.generics.filters import TogetherFilterSet
from iati.models import Document


class DocumentFilter(TogetherFilterSet):
    class Meta:
        model = Document
        fields = '__all__'
