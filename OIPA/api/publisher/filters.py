import django_filters
from iati_synchroniser.models import Publisher


class PublisherFilter(django_filters.FilterSet):
    """
    Filter publisher list
    """

    class Meta:
        model = Publisher
        fields = [
            'org_id',
            'org_abbreviate',
            'org_name']
