from django.apps import apps
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.codelist.filters import AllDjangoFilterBackend
from api.codelist.serializers import (
    CodelistItemSerializer, CodelistMetaSerializer
)
from api.generics.views import DynamicListView
from geodata.models import Region
from iati_synchroniser.models import Codelist


class CodelistMetaList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI codelists stored in OIPA.

    ## Result details

    Each result item contains full information about codelist including URI to
    codelist items.

    URI is constructed as follows: `/api/codelists/{codelistname}/`

    """
    queryset = Codelist.objects.all().order_by('name')
    serializer_class = CodelistMetaSerializer
    fields = ('name', 'items')
    pagination_class = None


class CodelistItemList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI codelist values stored in OIPA.

    ## request parameters

    - `code` (*optional*): Comma separated list of codes on the codelist.
    - `vocabulary` (*optional*): Comma separated list of .
    - `category` (*optional*): Comma separated list of categories (if
       applicable for the codelist).

    ## Ordering

    API request may include `ordering` parameter. This parameter controls the
    order in which results are returned.

    Results can be ordered by:

    - `name`

    The user may also specify reverse orderings by prefixing the field name
    with '-', like so: `-name`

    ## Result details

    Each item contains all information on the codelist items being shown.

    """
    queryset = Region.objects.none()
    filter_backends = (AllDjangoFilterBackend, OrderingFilter, )
    fields = ('code', 'name')
    codelistAppMap = {
        'Country': 'geodata',
        'Region': 'geodata',
    }
    pagination_class = None
    model_name_maps = {
        'CRSAddOtherFlags': 'OtherFlags',
        'IATIOrganisationIdentifier': 'OrganisationIdentifier'
    }

    @classmethod
    def model_name_camel(cls, name):
        names = name.split('-')
        if len(names) > 1:
            name = names[0] + names[1].capitalize()

        return name

    def get_app_label(self, model_name):
        if 'Vocabulary' in model_name:
            return 'iati_vocabulary'
        return self.codelistAppMap.get(model_name, 'iati_codelists')

    def get_queryset(self):
        model_name = self.kwargs.get('codelist', None)

        if not model_name:
            return self.queryset

        model_name = self.model_name_camel(model_name)

        app_label = self.get_app_label(model_name)

        model_name = self.model_name_maps.get(model_name, model_name)

        try:
            model_cls = apps.get_model(app_label, model_name)
        except LookupError:
            raise NotFound("Codelist not found")

        queryset = model_cls.objects.all()

        for f in model_cls._meta.get_fields():
            if f.many_to_one and f.related_model:
                queryset = queryset.select_related(f.name)

        return queryset

    def get_serializer_class(self):
        cms = CodelistItemSerializer
        # dummy, for some reason this method is called multiple times, first
        # time without a request class.
        cms.Meta.model = Region

        if hasattr(self, 'request'):
            model_name = self.kwargs.get('codelist', None)

            if not model_name:
                return cms
            # model_name = self.capitalize(model_name)

            model_name = self.model_name_maps.get(model_name, model_name)


            model_name = self.model_name_camel(model_name)

            app_label = self.get_app_label(model_name)
            cms.Meta.model = apps.get_model(app_label, model_name)

        return cms
