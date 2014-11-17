import iati
import factory


class TitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Title

    title = 'title factory'


class DescriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Description

    description = 'description factory'


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Activity
        django_get_or_create = ('id',)

    id = 'IATI-0001'
    total_budget = 50
    iati_identifier = 'IATI-0001'
    title_set = factory.RelatedFactory(TitleFactory, 'activity_id',)
    description_set = factory.RelatedFactory(DescriptionFactory, 'activity_id')
