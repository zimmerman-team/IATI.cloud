from django.test import TestCase
from iati.models import Activity
from iati.factory.utils import _create_test_activity


class ActivityModelTestCase(TestCase):

    def test_create_activity(self):
        self.assertEqual(Activity.objects.count(), 0)
        _create_test_activity(id='100000', iati_identifier='100000')
        self.assertIsNotNone(Activity.objects.get(pk='100000'))

    def test_delete_activity(self):
        activity = _create_test_activity(id='100000', iati_identifier='100000')
        activity.delete()
        self.assertEqual(Activity.objects.filter(pk='100000').count(), 0)

    def test_delete_related_activity(self):
        activity = _create_test_activity(id='100000', iati_identifier='100000')
        assert activity.relatedactivity_set.count() == 1  # _create_test_activity() creates 1 related activity

        # save related activity pk to query fresh object after deleting main activity
        related_activity = activity.relatedactivity_set.all()[0]
        related_activity_pk = related_activity.pk

        # Deleting an activity also deletes RelatedActivity but not the RelatedActivity.ref_activity instance
        activity.delete()
        self.assertEqual(Activity.objects.filter(pk='100000').count(), 0)
        self.assertEqual(Activity.objects.filter(pk=related_activity_pk).count(), 0)
