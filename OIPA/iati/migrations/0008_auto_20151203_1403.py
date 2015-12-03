# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0007_auto_20151127_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='activity_status',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.ActivityStatus', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='actual_end',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='actual_start',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='capital_spend',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='collaboration_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.CollaborationType', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='default_aid_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.AidType', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='default_currency',
            field=models.ForeignKey(related_name='default_currency', default=None, blank=True, to='iati_codelists.Currency', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='default_finance_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.FinanceType', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='default_flow_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.FlowType', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='default_tied_status',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.TiedStatus', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='end_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='planned_end',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='planned_start',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='scope',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.ActivityScope', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='budget_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='budget_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='commitment_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='commitment_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='disbursement_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='disbursement_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='expenditure_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='expenditure_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='incoming_funds_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, blank=True, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='ref',
            field=models.CharField(default=b'', max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='role',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.OrganisationRole', null=True),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.OrganisationType', null=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='budget_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='budget_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='commitment_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='commitment_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='disbursement_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='disbursement_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='expenditure_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='expenditure_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='incoming_funds_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypolicymarker',
            name='significance',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.PolicySignificance', null=True),
        ),
        migrations.AlterField(
            model_name='activityrecipientcountry',
            name='percentage',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityrecipientregion',
            name='percentage',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityreportingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, blank=True, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='activityreportingorganisation',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.OrganisationType', null=True),
        ),
        migrations.AlterField(
            model_name='activitysector',
            name='percentage',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitysector',
            name='sector',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Sector', null=True),
        ),
        migrations.AlterField(
            model_name='activitysector',
            name='vocabulary',
            field=models.ForeignKey(default=None, blank=True, to='iati_vocabulary.SectorVocabulary', null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='currency',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Currency', null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.BudgetType', null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='value_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='budgetitem',
            name='percentage',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='budget_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='budget_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='commitment_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='commitment_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='disbursement_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='disbursement_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='expenditure_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='expenditure_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='incoming_funds_currency',
            field=models.CharField(default=None, max_length=3, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='condition',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.ConditionType', null=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='type',
            field=models.ForeignKey(blank=True, to='iati_codelists.ContactType', null=True),
        ),
        migrations.AlterField(
            model_name='countrybudgetitem',
            name='percentage',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='currency',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Currency', null=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='interest_arrears',
            field=models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='interest_received',
            field=models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='principal_arrears',
            field=models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='principal_outstanding',
            field=models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='value_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanstatus',
            name='year',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='commitment_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='rate_1',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='rate_2',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='repayment_final_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='repayment_first_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='repayment_plan',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.LoanRepaymentPeriod', null=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='repayment_plan_text',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crsaddloanterms',
            name='repayment_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.LoanRepaymentType', null=True),
        ),
        migrations.AlterField(
            model_name='crsaddotherflags',
            name='other_flags_significance',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='description',
            name='type',
            field=models.ForeignKey(related_name='description_type', default=None, blank=True, to='iati_codelists.DescriptionType', null=True),
        ),
        migrations.AlterField(
            model_name='documentlink',
            name='file_format',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.FileFormat', null=True),
        ),
        migrations.AlterField(
            model_name='documentlinklanguage',
            name='language',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Language', null=True),
        ),
        migrations.AlterField(
            model_name='fss',
            name='extraction_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fss',
            name='phaseout_year',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fssforecast',
            name='value_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fssforecast',
            name='year',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='legacydata',
            name='iati_equivalent',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='legacydata',
            name='name',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='legacydata',
            name='value',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='exactness',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.GeographicExactness', null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='feature_designation',
            field=models.ForeignKey(related_name='feature_designation', default=None, blank=True, to='iati_codelists.LocationType', null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='location_class',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.GeographicLocationClass', null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='location_id_vocabulary',
            field=models.ForeignKey(related_name='location_id_vocabulary', default=None, blank=True, to='iati_vocabulary.GeographicVocabulary', null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='location_reach',
            field=models.ForeignKey(related_name='location_reach', default=None, blank=True, to='iati_codelists.GeographicLocationReach', null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='ref',
            field=models.CharField(default=b'', max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='locationadministrative',
            name='level',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='otheridentifier',
            name='type',
            field=models.ForeignKey(blank=True, to='iati_codelists.OtherIdentifierType', null=True),
        ),
        migrations.AlterField(
            model_name='planneddisbursement',
            name='budget_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.BudgetType', null=True),
        ),
        migrations.AlterField(
            model_name='planneddisbursement',
            name='currency',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Currency', null=True),
        ),
        migrations.AlterField(
            model_name='planneddisbursement',
            name='value_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='relatedactivity',
            name='ref_activity',
            field=models.ForeignKey(related_name='ref_activity', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='relatedactivity',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.RelatedActivityType', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.ResultType', null=True),
        ),
        migrations.AlterField(
            model_name='resultindicator',
            name='measure',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.IndicatorMeasure', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='aid_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.AidType', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.Currency', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='disbursement_channel',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.DisbursementChannel', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='finance_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.FinanceType', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='flow_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.FlowType', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='recipient_country',
            field=models.ForeignKey(default=None, blank=True, to='geodata.Country', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='recipient_region',
            field=models.ForeignKey(blank=True, to='geodata.Region', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='ref',
            field=models.CharField(default=b'', max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='tied_status',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.TiedStatus', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.ForeignKey(default=None, blank=True, to='iati_codelists.TransactionType', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='value_date',
            field=models.DateField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='organisation',
            field=models.ForeignKey(related_name='transaction_providing_organisation', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='provider_activity',
            field=models.ForeignKey(related_name='transaction_provider_activity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='provider_activity_ref',
            field=models.CharField(default=b'', max_length=200, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='organisation',
            field=models.ForeignKey(related_name='transaction_receiving_organisation', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='receiver_activity',
            field=models.ForeignKey(related_name='transaction_receiver_activity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='receiver_activity_ref',
            field=models.CharField(default=b'', max_length=200, null=True, db_index=True, blank=True),
        ),
    ]
