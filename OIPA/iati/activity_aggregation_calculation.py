from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.db.utils import IntegrityError as Integrity

from currency_convert import convert
from iati.models import Activity, ActivityAggregation, ActivityPlusChildAggregation, ChildAggregation
from iati.transaction.models import Transaction
from solr.activity.tasks import ActivityTaskIndexing


class ActivityAggregationCalculation():

    def parse_all_activity_aggregations(self):
        for activity in Activity.objects.all():
            self.parse_activity_aggregations(activity)

    def parse_activity_aggregations_by_source(self, dataset_id):
        for activity in Activity.objects.filter(dataset__id=dataset_id):
            self.parse_activity_aggregations(activity)

    def parse_activity_aggregations(self, activity):
        self.calculate_activity_aggregations(activity)
        self.calculate_child_aggregations(activity)
        self.calculate_activity_plus_child_aggregations(activity)
        self.update_parents_child_budgets(activity)
        try:
            activity.save()
        except Integrity():
            activity.update()

    def update_parents_child_budgets(self, activity):

        if activity.hierarchy != 1:
            # update the parent's child budgets
            parent_activity = activity.relatedactivity_set.filter(type__code=1)
            if len(parent_activity) and parent_activity[0].ref_activity:
                parent_activity = parent_activity[0].ref_activity
                try:
                    parent_activity.activity_aggregation
                except ObjectDoesNotExist:
                    self.calculate_activity_aggregations(parent_activity)
                self.calculate_child_aggregations(parent_activity)
                self.calculate_activity_plus_child_aggregations(
                    parent_activity)
                parent_activity.save()
                # After updating the parent activity, this should trigger
                # indexing as well.
                ActivityTaskIndexing(parent_activity, related=True).run()

    def set_aggregation(
            self,
            activity_aggregation,
            currency_field_name,
            value_field_name,
            value_usd_field_name,
            value_gbp_field_name,
            aggregation_object):
        """
        aggregation object contains: 0: currency, 1: date of transaction,
        2: value
        """

        currency = None
        default_currency = activity_aggregation.activity.default_currency_id

        value = (0, None)[len(aggregation_object) <= 0]
        value_usd = (0, None)[len(aggregation_object) <= 0]
        value_gbp = (0, None)[len(aggregation_object) <= 0]

        for agg_item in aggregation_object:
            currency = agg_item[0]
            if agg_item[2]:
                value = value + agg_item[2]
                conversion_currency = \
                    currency if currency else default_currency

                if conversion_currency:
                    converted_value_usd = round(convert.currency_from_to(
                        conversion_currency,
                        'USD',
                        agg_item[1],
                        agg_item[2]),
                        2)
                    value_usd = value_usd + converted_value_usd
                    converted_value_gbp = round(convert.currency_from_to(
                        conversion_currency,
                        'GBP',
                        agg_item[1],
                        agg_item[2]),
                        2)
                    value_gbp = value_gbp + converted_value_gbp

        if len(aggregation_object) > 1:
            # mixed currencies, set as None
            currency = None

        setattr(activity_aggregation, currency_field_name, currency)
        setattr(activity_aggregation, value_field_name, value)
        setattr(activity_aggregation, value_usd_field_name, value_usd)
        setattr(activity_aggregation, value_gbp_field_name, value_gbp)

        return activity_aggregation

    def calculate_activity_aggregations(self, activity):
        """

        """

        try:
            activity_aggregation = activity.activity_aggregation
        except ObjectDoesNotExist:
            activity_aggregation = ActivityAggregation()
            activity_aggregation.activity = activity

        budget_total = activity.budget_set.values_list(
            'currency', 'value_date').annotate(Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'budget_currency',
            'budget_value',
            'budget_value_usd',
            'budget_value_gbp',
            budget_total)

        incoming_fund_total = activity.transaction_set.filter(
            transaction_type=1).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'incoming_funds_currency',
            'incoming_funds_value',
            'incoming_funds_value_usd',
            'incoming_funds_value_gbp',
            incoming_fund_total)

        commitment_total = activity.transaction_set.filter(
            transaction_type=2).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'commitment_currency',
            'commitment_value',
            'commitment_value_usd',
            'commitment_value_gbp',
            commitment_total)

        disbursement_total = activity.transaction_set.filter(
            transaction_type=3).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'disbursement_currency',
            'disbursement_value',
            'disbursement_value_usd',
            'disbursement_value_gbp',
            disbursement_total)

        expenditure_total = activity.transaction_set.filter(
            transaction_type=4).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'expenditure_currency',
            'expenditure_value',
            'expenditure_value_usd',
            'expenditure_value_gbp',
            expenditure_total)

        interest_payment_total = activity.transaction_set.filter(
            transaction_type=5).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'interest_payment_currency',
            'interest_payment_value',
            'interest_payment_value_usd',
            'interest_payment_value_gbp',
            interest_payment_total)

        loan_repayment_total = activity.transaction_set.filter(
            transaction_type=6).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'loan_repayment_currency',
            'loan_repayment_value',
            'loan_repayment_value_usd',
            'loan_repayment_value_gbp',
            loan_repayment_total)

        reimbursement_total = activity.transaction_set.filter(
            transaction_type=7).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'reimbursement_currency',
            'reimbursement_value',
            'reimbursement_value_usd',
            'reimbursement_value_gbp',
            reimbursement_total)

        purchase_of_equity_total = activity.transaction_set.filter(
            transaction_type=8).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'purchase_of_equity_currency',
            'purchase_of_equity_value',
            'purchase_of_equity_value_usd',
            'purchase_of_equity_value_gbp',
            purchase_of_equity_total)

        sale_of_equity_total = activity.transaction_set.filter(
            transaction_type=9).values_list('currency',
                                            'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'sale_of_equity_currency',
            'sale_of_equity_value',
            'sale_of_equity_value_usd',
            'sale_of_equity_value_gbp',
            sale_of_equity_total)

        credit_guarantee_total = activity.transaction_set.filter(
            transaction_type=10).values_list('currency',
                                             'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'credit_guarantee_currency',
            'credit_guarantee_value',
            'credit_guarantee_value_usd',
            'credit_guarantee_value_gbp',
            credit_guarantee_total)

        incoming_commitment_total = activity.transaction_set.filter(
            transaction_type=11).values_list('currency',
                                             'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'incoming_commitment_currency',
            'incoming_commitment_value',
            'incoming_commitment_value_usd',
            'incoming_commitment_value_gbp',
            incoming_commitment_total)

        outgoing_pledge_total = activity.transaction_set.filter(
            transaction_type=12).values_list('currency',
                                             'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'outgoing_pledge_currency',
            'outgoing_pledge_value',
            'outgoing_pledge_value_usd',
            'outgoing_pledge_value_gbp',
            outgoing_pledge_total)

        incoming_pledge_total = activity.transaction_set.filter(
            transaction_type=13).values_list('currency',
                                             'transaction_date').annotate(
            Sum('value'))
        activity_aggregation = self.set_aggregation(
            activity_aggregation,
            'incoming_pledge_currency',
            'incoming_pledge_value',
            'incoming_pledge_value_usd',
            'incoming_pledge_value_gbp',
            incoming_pledge_total)

        # raises IntegrityError when an activity appears in multiple sources
        # and they are parsed at the same time TODO find solution that's less
        # ugly
        try:
            activity_aggregation.save()
        except IntegrityError:
            pass

    def calculate_child_budget_aggregation(
            self,
            activity):

        return Activity.objects\
            .filter(
                relatedactivity__ref=activity.iati_identifier,
                relatedactivity__type=1,)\
            .filter(budget__currency__isnull=False)\
            .values_list('budget__currency', 'budget__value_date')\
            .annotate(total_budget=Sum('budget__value'))

    def calculate_child_transaction_aggregation(
            self,
            activity,
            transaction_type):

        return Transaction.objects .filter(
            activity__relatedactivity__ref=activity.iati_identifier,
            activity__relatedactivity__type=1) .filter(
            transaction_type=transaction_type) .filter(
            currency__isnull=False) .values_list('currency',
                                                 'transaction_date') .annotate(
                Sum('value'))

    def calculate_child_aggregations(self, activity):

        try:
            child_aggregation = activity.child_aggregation
        except ObjectDoesNotExist:
            child_aggregation = ChildAggregation()
            child_aggregation.activity = activity

        budget_total = self.calculate_child_budget_aggregation(activity)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'budget_currency',
            'budget_value',
            'budget_value_usd',
            'budget_value_gbp',
            budget_total)

        incoming_fund_total = self.calculate_child_transaction_aggregation(
            activity, 1)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'incoming_funds_currency',
            'incoming_funds_value',
            'incoming_funds_value_usd',
            'incoming_funds_value_gbp',
            incoming_fund_total)

        commitment_total = self.calculate_child_transaction_aggregation(
            activity, 2)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'commitment_currency',
            'commitment_value',
            'commitment_value_usd',
            'commitment_value_gbp',
            commitment_total)

        disbursement_total = self.calculate_child_transaction_aggregation(
            activity, 3)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'disbursement_currency',
            'disbursement_value',
            'disbursement_value_usd',
            'disbursement_value_gbp',
            disbursement_total)

        expenditure_total = self.calculate_child_transaction_aggregation(
            activity, 4)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'expenditure_currency',
            'expenditure_value',
            'expenditure_value_usd',
            'expenditure_value_gbp',
            expenditure_total)

        interest_payment_total = self.calculate_child_transaction_aggregation(
            activity, 5)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'interest_payment_currency',
            'interest_payment_value',
            'interest_payment_value_usd',
            'interest_payment_value_gbp',
            interest_payment_total)

        loan_repayment_total = self.calculate_child_transaction_aggregation(
            activity, 6)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'loan_repayment_currency',
            'loan_repayment_value',
            'loan_repayment_value_usd',
            'loan_repayment_value_gbp',
            loan_repayment_total)

        reimbursement_total = self.calculate_child_transaction_aggregation(
            activity, 7)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'reimbursement_currency',
            'reimbursement_value',
            'reimbursement_value_usd',
            'reimbursement_value_gbp',
            reimbursement_total)

        purchase_of_equity_total = self\
            .calculate_child_transaction_aggregation(
                activity, 8)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'purchase_of_equity_currency',
            'purchase_of_equity_value',
            'purchase_of_equity_value_usd',
            'purchase_of_equity_value_gbp',
            purchase_of_equity_total)

        sale_of_equity_total = self.calculate_child_transaction_aggregation(
            activity, 9)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'sale_of_equity_currency',
            'sale_of_equity_value',
            'sale_of_equity_value_usd',
            'sale_of_equity_value_gbp',
            sale_of_equity_total)

        credit_guarantee_total = self.calculate_child_transaction_aggregation(
            activity, 10)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'credit_guarantee_currency',
            'credit_guarantee_value',
            'credit_guarantee_value_usd',
            'credit_guarantee_value_gbp',
            credit_guarantee_total)

        incoming_commitment_total = self\
            .calculate_child_transaction_aggregation(
                activity, 11)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'incoming_commitment_currency',
            'incoming_commitment_value',
            'incoming_commitment_value_usd',
            'incoming_commitment_value_gbp',
            incoming_commitment_total)

        outgoing_pledge_total = self.calculate_child_transaction_aggregation(
            activity, 12)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'outgoing_pledge_currency',
            'outgoing_pledge_value',
            'outgoing_pledge_value_usd',
            'outgoing_pledge_value_gbp',
            outgoing_pledge_total)

        incoming_pledge_total = self\
            .calculate_child_transaction_aggregation(
                activity, 13)
        child_aggregation = self.set_aggregation(
            child_aggregation,
            'incoming_pledge_currency',
            'incoming_pledge_value',
            'incoming_pledge_value_usd',
            'incoming_pledge_value_gbp',
            incoming_pledge_total)

        # raises IntegrityError when an activity appears in multiple sources
        # and they are parsed at the same time TODO find solution that's less
        # ugly
        try:
            child_aggregation.save()
        except IntegrityError:
            pass

    def update_total_aggregation(
            self,
            activity,
            total_aggregation,
            aggregation_type):
        """

        """
        activity_value = getattr(
            activity.activity_aggregation, aggregation_type + '_value')
        activity_value_usd = getattr(
            activity.activity_aggregation, aggregation_type + '_value_usd') or 0  # NOQA: E501
        activity_value_gbp = getattr(
            activity.activity_aggregation, aggregation_type + '_value_gbp') or 0  # NOQA: E501
        activity_currency = getattr(
            activity.activity_aggregation, aggregation_type + '_currency')
        child_value = getattr(activity.child_aggregation,
                              aggregation_type + '_value')
        child_value_usd = getattr(activity.child_aggregation,
                                  aggregation_type + '_value_usd') or 0
        child_value_gbp = getattr(activity.child_aggregation,
                                  aggregation_type + '_value_gbp') or 0
        child_currency = getattr(
            activity.child_aggregation, aggregation_type + '_currency')

        if (activity_value is not None) and (child_value is not None):
            total_aggregation_value = activity_value + child_value
            total_aggregation_value_usd = activity_value_usd + child_value_usd
            total_aggregation_value_gbp = activity_value_gbp + child_value_gbp
            total_aggregation_currency = activity_currency
        elif (activity_value is not None) and (child_value is None):
            total_aggregation_value = activity_value
            total_aggregation_value_usd = activity_value_usd
            total_aggregation_value_gbp = activity_value_gbp
            total_aggregation_currency = activity_currency
        elif (activity_value is None) and (child_value is not None):
            total_aggregation_value = child_value
            total_aggregation_value_usd = child_value_usd
            total_aggregation_value_gbp = child_value_gbp
            total_aggregation_currency = child_currency
        else:
            total_aggregation_value = None
            total_aggregation_value_usd = None
            total_aggregation_value_gbp = None
            total_aggregation_currency = None

        setattr(total_aggregation, aggregation_type +
                '_currency', total_aggregation_currency)
        setattr(total_aggregation, aggregation_type +
                '_value', total_aggregation_value)
        setattr(total_aggregation, aggregation_type +
                '_value_usd', total_aggregation_value_usd)
        setattr(total_aggregation, aggregation_type +
                '_value_gbp', total_aggregation_value_gbp)

        return total_aggregation

    def calculate_activity_plus_child_aggregations(self, activity):

        try:
            total_aggregation = activity.activity_plus_child_aggregation
        except ObjectDoesNotExist:
            total_aggregation = ActivityPlusChildAggregation()
            total_aggregation.activity = activity

        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'budget')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'incoming_funds')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'commitment')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'disbursement')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'expenditure')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'interest_payment')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'loan_repayment')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'reimbursement')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'purchase_of_equity')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'sale_of_equity')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'credit_guarantee')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'incoming_commitment')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'outgoing_pledge')
        total_aggregation = self.update_total_aggregation(
            activity, total_aggregation, 'incoming_pledge')

        # raises IntegrityError when an activity appears in multiple sources
        # and they are parsed at the same time TODO find solution that's less
        # ugly
        try:
            total_aggregation.save()
        except IntegrityError:
            pass
