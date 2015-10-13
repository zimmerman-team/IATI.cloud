from haystack import indexes
from models import Narrative,Description,Title,Activity,ActivityRecipientCountry,ActivityRecipientRegion,ActivitySector,ActivityParticipatingOrganisation,Organisation,DocumentLink

# class NarrativeIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return Narrative

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class DesriptionIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return Description

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class TitleIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return Title

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

"""
  -activity id
    -title
    -description
    -participating organisation name
    -reporting organisation name
    -country name
    -region name
    -sector name
    -documentlink title
"""
class ActivityIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    activity_id = indexes.CharField(model_attr='iati_identifier')
    title = indexes.CharField(use_template=True)
    description = indexes.CharField(use_template=True)
    country = indexes.CharField(use_template=True)
    reporting_org = indexes.CharField(use_template=True)
    region = indexes.CharField(use_template=True)
    sector = indexes.CharField(use_template=True)
    documentlink_title = indexes.CharField(use_template=True)
    participating_org = indexes.CharField(use_template=True)
    last_updated =  indexes.DateTimeField(model_attr='last_updated')

    def get_model(self):
        return Activity

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_updated_field(self):
    	return 'last_updated'

# class ActivityRecipientCountryIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return ActivityRecipientCountry

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class ActivityRecipientRegionIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return ActivityRecipientRegion

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class ActivitySectorIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return ActivitySector

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class ActivityParticipatingOrganisationIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return ActivityParticipatingOrganisation

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

# class DocumentLinkIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
    

#     def get_model(self):
#         return DocumentLink

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()








