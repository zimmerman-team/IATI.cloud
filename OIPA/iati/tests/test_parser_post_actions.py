from iati.tests.test_parser_fields import ParserSetupTestCase
from unittest import skip


class PostSaveActivityTestCase(ParserSetupTestCase):
    """
    2.01: post activity actions called
    """

    @skip('NotImplemented')
    def test_post_save_activity(self):
        """
        Check if sets related activities and activity aggregations
        """

    @skip('NotImplemented')
    def set_related_activities(self):
        """
        Check if related activities are linked to the current activity
        and the current activity is related to another activity
        """

    @skip('NotImplemented')
    def set_transaction_provider_receiver_activity(self):
        """
        Check if references to/from provider/receiver activity are set in transactions
        """

    @skip('NotImplemented')
    def set_derived_activity_dates(self):
        """
        Check if derived (actual > planned) dates are set correctly
        """

    @skip('NotImplemented')
    def test_set_activity_aggregations(self):
        """
        Check if calculated budget / transaction etc values are correct
        """

    @skip('NotImplemented')
    def test_update_activity_search_index(self):
        """
        Check if dates are set correctly
        """


class PostSaveFileTestCase(ParserSetupTestCase):
    """
    2.01: post save activity actions called
    """

    @skip('NotImplemented')
    def test_post_save_file(self):
        """
        Check if sets related activities and activity aggregations
        """

    @skip('NotImplemented')
    def test_delete_removed_activities(self):
        """
        Check if related activities are linked to the current activity
        and the current activity is related to another activity
        """

