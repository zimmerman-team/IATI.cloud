from haystack import indexes
from models import Activity


class ActivityIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.MultiValueField(document=True)
    activity_id = indexes.CharField(model_attr='iati_identifier', default='')
    title = indexes.MultiValueField()
    description = indexes.MultiValueField()
    reporting_org = indexes.MultiValueField()
    recipient_country = indexes.MultiValueField()
    recipient_region = indexes.MultiValueField()
    sector = indexes.MultiValueField()
    document_link = indexes.MultiValueField()
    participating_org = indexes.MultiValueField()
    last_updated_model = indexes.DateTimeField(model_attr='last_updated_model')

    def get_model(self):
        return Activity

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_updated_field(self):
        return 'last_updated_model'

    def prepare(self, obj):
        self.prepared_data = super(ActivityIndex, self).prepare(obj)
        
        texts = []
        texts.append(self.prepared_data['activity_id'])
        texts.extend(self.prepare_title(obj))
        texts.extend(self.prepare_description(obj))
        texts.extend(self.prepare_recipient_country(obj))
        texts.extend(self.prepare_recipient_region(obj))
        texts.extend(self.prepare_sector(obj))
        texts.extend(self.prepare_document_link(obj))
        texts.extend(self.prepare_participating_org(obj))
        self.prepared_data['text'] = texts

        return self.prepared_data

    def prepare_title(self, obj):
        return [narrative.content for narrative in obj.title.narratives.all()]

    def prepare_description(self, obj):
        text = []
        for description in obj.description_set.all():
            for narrative in description.narratives.all():
                text.append(narrative.content)
        return text

    def prepare_reporting_org(self, obj):
        text = []
        for reporting_org in obj.reporting_organisations.all():
            text.append(reporting_org.ref)
            for narrative in reporting_org.narratives.all():
                text.append(narrative.content)
        return text

    def prepare_recipient_country(self, obj):
        text = []
        for country in obj.recipient_country.all():
            text.append(country.code)
            text.append(country.name)
        return text

    def prepare_recipient_region(self, obj):
        text = []
        for region in obj.recipient_region.all():
            text.append(region.code)
            text.append(region.name)
        return text

    def prepare_sector(self, obj):
        text = []
        for sector in obj.sector.all():
            text.append(sector.code)
            text.append(sector.name)
        return text

    def prepare_document_link(self, obj):
        text = []
        for document_link in obj.documentlink_set.all():
            text.append(document_link.url)
            for cat in document_link.categories.all():
                text.append(cat.name)
            for title in document_link.documentlinktitle_set.all():
                for narrative in title.narratives.all():
                    text.append(narrative.content)
        return text

    def prepare_participating_org(self, obj):
        text = []
        for participating_org in obj.participating_organisations.all():
            text.append(participating_org.ref)
            for narrative in participating_org.narratives.all():
                    text.append(narrative.content)
        return text

