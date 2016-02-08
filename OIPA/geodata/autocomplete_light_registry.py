import autocomplete_light.shortcuts as al
from geodata.models import Country, Region


al.register(Country,
    search_fields=['code', 'name'],
    attrs={'placeholder': 'Search country',
           'class': 'narrative_activity_field',
           'data-autocomplete-minimum-characters': 1},
    widget_attrs={'data-widget-maximum-values': 4, 'class': 'modern-style narrative_activity_field'},)


al.register(Region,
    search_fields=['code', 'name'],
    attrs={'placeholder': 'Search region',
           'class': 'narrative_activity_field',
           'data-autocomplete-minimum-characters': 1},
    widget_attrs={'data-widget-maximum-values': 4, 'class': 'modern-style narrative_activity_field'},)
