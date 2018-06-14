from django import forms
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ObjectDoesNotExist

from django.forms import ModelForm

from iati.models import (Activity, ActivityParticipatingOrganisation, ActivityReportingOrganisation, DocumentLink,
                         Location, Narrative, RelatedActivity)


class NarrativeForm(ModelForm):
    activity = forms.ModelChoiceField(
        Activity.objects.none(), required=False, empty_label='----')

    class Meta(object):
        model = Narrative
        fields = ('activity', 'language', 'content')

    def clean(self):
        # Then call the clean() method of the super  class
        cleaned_data = super(NarrativeForm, self).clean()
        # activity somehow is invalidated here, so re-setting it to the correct activity
        try:
            cleaned_data['activity'] = self.instance.activity
        except ObjectDoesNotExist:
            pass
        # Finally, return the cleaned_data
        return cleaned_data

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


class DocumentLinkTitleForm(ModelForm):

    def save(self, commit=True):
        instance = super(DocumentLinkTitleForm, self).save(commit=False)
        instance.save()
        return instance


class DocumentLinkForm(ModelForm):
    class Meta:
        model = DocumentLink
        exclude = ['']
        widgets = {'url': forms.TextInput(
            attrs={'class': 'admin-charfield-more-width'})}

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
                data['point_pos'] = GEOSGeometry(
                    Point(longitude, latitude), srid=4326)
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
        if 'point_pos' in self.errors:
            del self.errors['point_pos']
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            try:
                lat, lng = float(data.pop("latitude", None)), float(
                    data.pop("longitude", None))
                data['point_pos'] = GEOSGeometry(Point(lng, lat), srid=4326)
            except (TypeError, ValueError):
                data['point_pos'] = None

        if not (data.get("point_pos") or data.get("latitude")):
            raise forms.ValidationError(
                {"latitude": "Coordinates is required"})
        return data


class RelatedActivityForm(ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {'ref': forms.HiddenInput()}

    def clean(self):
        data = super(RelatedActivityForm, self).clean()
        if data['ref_activity']:
            data['ref'] = data['ref_activity'].id
        return data
