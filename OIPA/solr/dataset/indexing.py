
from rest_framework.renderers import JSONRenderer

from api.publisher.serializers import PublisherSerializer
from solr.indexing import BaseIndexing
from solr.utils import get_child_attr, value_string


class DatasetIndexing(BaseIndexing):

    def dataset_publisher(self):
        publisher = get_child_attr(self.record, 'publisher')
        if publisher:
            self.add_field(
                'publisher',
                JSONRenderer().render(
                    PublisherSerializer(
                        fields=[
                            'iati_id',
                            'publisher_iati_id',
                            'display_name',
                            'name',
                            'activity_count'
                        ],
                        instance=publisher
                    ).data
                ).decode()
            )

            self.add_field('publisher_iati_id', publisher.publisher_iati_id)
            self.add_field('publisher_name', publisher.name)
            self.add_field('publisher_display_name', publisher.display_name)

    def dataset(self):
        dataset = self.record

        self.add_field('id', dataset.id)
        self.add_field('name', dataset.name)
        self.add_field('title', dataset.title)
        self.add_field('filetype', dataset.filetype)
        self.add_field(
            'date_created',
            value_string(dataset.date_created).split(' ')[0]
        )
        self.add_field(
            'date_updated',
            value_string(dataset.date_updated).split(' ')[0]
        )
        self.add_field('iati_version', dataset.iati_version)
        self.add_field('source_url', dataset.source_url)

        self.dataset_publisher()

    def to_representation(self, dataset):
        self.record = dataset

        self.indexing = {}
        self.representation = {}

        self.dataset()
        self.build()

        return self.representation
