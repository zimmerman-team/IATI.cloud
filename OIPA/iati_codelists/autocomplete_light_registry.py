import autocomplete_light.shortcuts as al
from iati_codelists.models import Currency, Language, Sector, FileFormat

# This will generate a PersonAutocomplete class.
al.register(Currency,
    # Just like in ModelAdmin.search_fields.
    search_fields=['code', 'name'],
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'Search currency',
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery.
        'data-autocomplete-minimum-characters': 1,
    },
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 4,
        # Enable modern-style widget !
        'class': 'modern-style',
    },
)

al.register(Language,
    search_fields=['code', 'name'],
    attrs={'placeholder': 'Search language', 'data-autocomplete-minimum-characters': 1, },
    widget_attrs={'data-widget-maximum-values': 4, 'class': 'modern-style'},)


al.register(Sector,
    search_fields=['code', 'name'],
    attrs={'placeholder': 'Search sector', 'data-autocomplete-minimum-characters': 1, },
    widget_attrs={'data-widget-maximum-values': 4, 'class': 'modern-style'},)

al.register(FileFormat,
    search_fields=['code', 'name'],
    attrs={'placeholder': 'Search file format', 'data-autocomplete-minimum-characters': 1, },
    widget_attrs={'data-widget-maximum-values': 4, 'class': 'modern-style'},)
