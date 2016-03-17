from django import forms
from autocomplete_light import forms as autocomplete_forms

from iati.models import Narrative
from iati.models import Activity
from iati.models import ActivityReportingOrganisation
from iati.models import ActivityParticipatingOrganisation
from iati.models import DocumentLink
from iati.models import Location
from iati.models import RelatedActivity
from django.contrib.gis.geos import Point


class NarrativeForm(autocomplete_forms.ModelForm):
    activity = forms.ModelChoiceField(Activity.objects.none(), required=False, empty_label='----')

    class Meta(object):
        model = Narrative
        fields = ('activity', 'language', 'content')

    def save(self, commit=True):
        if not self.instance.activity_id:
            self.instance.activity = self.cleaned_data['activity']
        instance = super(NarrativeForm, self).save(commit=False)
        instance.save()
        return instance


class ActivityReportingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = ActivityReportingOrganisation
        exclude = []
        widgets = {'normalized_ref': forms.HiddenInput()}

    def clean(self):
        if self.cleaned_data['ref']:
            self.cleaned_data['normalized_ref'] = self.cleaned_data['ref']
        data = super(ActivityReportingOrganisationForm, self).clean()

        return data


class ActivityParticipatingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = ActivityParticipatingOrganisation
        exclude = []
        widgets = {
            'normalized_ref': forms.HiddenInput(),
            'primary_name': forms.HiddenInput()}

    def clean(self):
        data = super(ActivityParticipatingOrganisationForm, self).clean()
        if data['ref']:
            data['normalized_ref'] = data['ref']
        return data


class DocumentLinkTitleForm(autocomplete_forms.ModelForm):

    def save(self, commit=True):
        instance = super(DocumentLinkTitleForm, self).save(commit=False)
        instance.save()
        return instance


class DocumentLinkForm(autocomplete_forms.ModelForm):
    class Meta:
        model = DocumentLink
        exclude = ['']
        widgets = {'url': forms.TextInput(attrs={'class': 'admin-charfield-more-width'})}

    def save(self, commit=True):
        instance = super(DocumentLinkForm, self).save(commit=False)
        instance.save()
        return instance



class LocationForm(forms.ModelForm):

    latitude = forms.DecimalField(
        label='latitude',
        min_value=-90,
        max_value=90,
        required=True,
    )
    longitude = forms.DecimalField(
        label='longitude',
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta(object):
        model = Location
        exclude = []
        widgets = {'point_pos': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        if args:
            data = args[0]
            if data['latitude'] and data['longitude']:
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                data['point_pos'] = Point(longitude, latitude)

        try:
            coordinates = kwargs['instance'].point_pos.tuple
            initial = kwargs.get('initial', {})
            initial['longitude'] = coordinates[0]
            initial['latitude'] = coordinates[1]
            kwargs['initial'] = initial
        except (KeyError, AttributeError):
            pass
        super(LocationForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(LocationForm, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            try:
                lat, lng = float(data.pop("latitude", None)), float(data.pop("longitude", None))
                data['point_pos'] = Point(lng, lat)
            except (TypeError, ValueError):
                data['point_pos'] = None

        if not (data.get("point_pos") or data.get("latitude")):
            raise forms.ValidationError({"point_pos": "Coordinates is required"})
        return data


class RelatedActivityForm(autocomplete_forms.ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {'ref': forms.HiddenInput()}


    def clean(self):
        data = super(RelatedActivityForm, self).clean()
        if data['ref_activity']:
            data['ref'] = data['ref_activity'].id
        return data
