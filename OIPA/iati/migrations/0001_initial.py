# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('iati_vocabulary', '0001_initial'),
        ('iati_codelists', '0001_initial'),
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.CharField(max_length=150, serialize=False, primary_key=True)),
                ('iati_identifier', models.CharField(max_length=150)),
                ('hierarchy', models.SmallIntegerField(default=1, null=True, choices=[(1, 'Parent'), (2, 'Child')])),
                ('last_updated_datetime', models.CharField(default=b'', max_length=100)),
                ('default_lang', models.CharField(max_length=2)),
                ('linked_data_uri', models.CharField(default=b'', max_length=100)),
                ('secondary_publisher', models.BooleanField(default=False)),
                ('xml_source_ref', models.CharField(default=b'', max_length=200)),
                ('capital_spend', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('has_conditions', models.BooleanField(default=True)),
                ('activity_status', models.ForeignKey(default=None, to='iati_codelists.ActivityStatus', null=True)),
                ('collaboration_type', models.ForeignKey(default=None, to='iati_codelists.CollaborationType', null=True)),
                ('default_aid_type', models.ForeignKey(default=None, to='iati_codelists.AidType', null=True)),
                ('default_currency', models.ForeignKey(related_name='default_currency', default=None, to='iati_codelists.Currency', null=True)),
                ('default_finance_type', models.ForeignKey(default=None, to='iati_codelists.FinanceType', null=True)),
                ('default_flow_type', models.ForeignKey(default=None, to='iati_codelists.FlowType', null=True)),
                ('default_tied_status', models.ForeignKey(default=None, to='iati_codelists.TiedStatus', null=True)),
                ('iati_standard_version', models.ForeignKey(to='iati_codelists.Version')),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
        ),
        migrations.CreateModel(
            name='ActivityDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_date', models.DateField(default=b'1970-01-01')),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('type', models.ForeignKey(to='iati_codelists.ActivityDateType')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityParticipatingOrganisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default=b'')),
                ('activity', models.ForeignKey(related_name='participating_organisations', to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityPolicyMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('policy_marker', models.ForeignKey(related_name='policy_marker_related', default=None, to='iati_codelists.PolicyMarker', null=True)),
                ('policy_significance', models.ForeignKey(default=None, to='iati_codelists.PolicySignificance', null=True)),
                ('vocabulary', models.ForeignKey(default=None, to='iati_vocabulary.Vocabulary', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityRecipientCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('country', models.ForeignKey(to='geodata.Country')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityRecipientRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('region', models.ForeignKey(to='geodata.Region')),
            ],
        ),
        migrations.CreateModel(
            name='ActivitySearchData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_identifier', models.CharField(max_length=150, db_index=True)),
                ('search_description', models.TextField(max_length=80000)),
                ('search_title', models.TextField(max_length=80000)),
                ('search_country_name', models.TextField(max_length=80000)),
                ('search_region_name', models.TextField(max_length=80000)),
                ('search_sector_name', models.TextField(max_length=80000)),
                ('search_participating_organisation_name', models.TextField(max_length=80000)),
                ('search_reporting_organisation_name', models.TextField(max_length=80000)),
                ('search_documentlink_title', models.TextField(max_length=80000)),
                ('activity', models.OneToOneField(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='ActivitySector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('sector', models.ForeignKey(default=None, to='iati_codelists.Sector', null=True)),
                ('vocabulary', models.ForeignKey(default=None, to='iati_vocabulary.Vocabulary', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityWebsite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.CharField(default=b'', max_length=50)),
                ('period_end', models.CharField(default=b'', max_length=50)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('value_date', models.DateField(default=None, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('currency', models.ForeignKey(default=None, to='iati_codelists.Currency', null=True)),
                ('type', models.ForeignKey(default=None, to='iati_codelists.BudgetType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'', max_length=50)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetItemDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget_item', models.ForeignKey(to='iati.BudgetItem')),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('type', models.ForeignKey(default=None, to='iati_codelists.ConditionType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person_name', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('organisation', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('telephone', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('email', models.TextField(default=b'', null=True, blank=True)),
                ('mailing_address', models.TextField(default=b'', null=True, blank=True)),
                ('website', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('job_title', models.CharField(default=b'', max_length=150, null=True, blank=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('contact_type', models.ForeignKey(default=None, blank=True, to='iati_codelists.ContactType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfoDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfoJobTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfoMailingAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfoOrganisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfoPersonName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
        ),
        migrations.CreateModel(
            name='CountryBudgetItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vocabulary_text', models.CharField(default=b'', max_length=255)),
                ('code', models.CharField(default=b'', max_length=50)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('description', models.TextField(default=b'')),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('vocabulary', models.ForeignKey(to='iati_vocabulary.BudgetIdentifierVocabulary', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrsAdd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='CrsAddLoanStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=None, null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('interest_received', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2)),
                ('principal_outstanding', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2)),
                ('principal_arrears', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2)),
                ('interest_arrears', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2)),
                ('crs_add', models.ForeignKey(to='iati.CrsAdd')),
                ('currency', models.ForeignKey(default=None, to='iati_codelists.Currency', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrsAddLoanTerms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate_1', models.IntegerField(default=None, null=True)),
                ('rate_2', models.IntegerField(default=None, null=True)),
                ('repayment_plan_text', models.TextField(default=b'', null=True)),
                ('commitment_date', models.DateField(default=None, null=True)),
                ('repayment_first_date', models.DateField(default=None, null=True)),
                ('repayment_final_date', models.DateField(default=None, null=True)),
                ('crs_add', models.ForeignKey(to='iati.CrsAdd')),
                ('repayment_plan', models.ForeignKey(default=None, to='iati_codelists.LoanRepaymentPeriod', null=True)),
                ('repayment_type', models.ForeignKey(default=None, to='iati_codelists.LoanRepaymentType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrsAddOtherFlags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('other_flags_significance', models.IntegerField(default=None, null=True)),
                ('crs_add', models.ForeignKey(to='iati.CrsAdd')),
                ('other_flags', models.ForeignKey(to='iati_codelists.OtherFlags')),
            ],
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('type', models.ForeignKey(related_name='description_type', default=None, to='iati_codelists.DescriptionType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(max_length=500)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('categories', models.ManyToManyField(to='iati_codelists.DocumentCategory')),
                ('file_format', models.ForeignKey(default=None, to='iati_codelists.FileFormat', null=True)),
                ('language', models.ForeignKey(default=None, to='iati_codelists.Language', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentLinkTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_link', models.ForeignKey(to='iati.DocumentLink')),
            ],
        ),
        migrations.CreateModel(
            name='Fss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extraction_date', models.DateField(default=None, null=True)),
                ('priority', models.BooleanField(default=False)),
                ('phaseout_year', models.IntegerField(null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='FssForecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('currency', models.ForeignKey(to='iati_codelists.Currency')),
                ('fss', models.ForeignKey(to='iati.Fss')),
            ],
        ),
        migrations.CreateModel(
            name='LegacyData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, null=True)),
                ('value', models.CharField(max_length=200, null=True)),
                ('iati_equivalent', models.CharField(max_length=150, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(default=b'', max_length=200)),
                ('type_description', models.CharField(default=b'', max_length=200)),
                ('adm_country_adm1', models.CharField(default=b'', max_length=100)),
                ('adm_country_adm2', models.CharField(default=b'', max_length=100)),
                ('adm_country_name', models.CharField(default=b'', max_length=200)),
                ('adm_code', models.CharField(default=b'', max_length=255, null=True)),
                ('adm_level', models.IntegerField(default=None, null=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('longitude', models.CharField(default=b'', max_length=70)),
                ('gazetteer_entry', models.CharField(default=b'', max_length=70)),
                ('location_id_code', models.CharField(default=b'', max_length=255)),
                ('point_srs_name', models.CharField(default=b'', max_length=255)),
                ('point_pos', models.CharField(default=b'', max_length=255)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('adm_country_iso', models.ForeignKey(default=None, to='geodata.Country', null=True)),
                ('adm_vocabulary', models.ForeignKey(related_name='administrative_vocabulary', default=None, to='iati_vocabulary.GeographicVocabulary', null=True)),
                ('description_type', models.ForeignKey(default=None, to='iati_codelists.DescriptionType', null=True)),
                ('exactness', models.ForeignKey(default=None, to='iati_codelists.GeographicExactness', null=True)),
                ('feature_designation', models.ForeignKey(related_name='feature_designation', default=None, to='iati_codelists.LocationType', null=True)),
                ('gazetteer_ref', models.ForeignKey(default=None, to='iati_codelists.GazetteerAgency', null=True)),
                ('location_class', models.ForeignKey(default=None, to='iati_codelists.GeographicLocationClass', null=True)),
                ('location_id_vocabulary', models.ForeignKey(related_name='location_id_vocabulary', default=None, to='iati_vocabulary.GeographicVocabulary', null=True)),
                ('location_reach', models.ForeignKey(default=None, to='iati_codelists.GeographicLocationReach', null=True)),
                ('precision', models.ForeignKey(default=None, to='iati_codelists.GeographicalPrecision', null=True)),
                ('type', models.ForeignKey(related_name='deprecated_location_type', default=None, to='iati_codelists.LocationType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocationActivityDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
        ),
        migrations.CreateModel(
            name='LocationDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
        ),
        migrations.CreateModel(
            name='LocationName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Narrative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.CharField(max_length=250, null=True, verbose_name=b'related object')),
                ('iati_identifier', models.CharField(max_length=150, null=True, verbose_name=b'iati_identifier')),
                ('content', models.TextField(null=True, blank=True)),
                ('content_type', models.ForeignKey(verbose_name=b'xml Parent', blank=True, to='contenttypes.ContentType', null=True)),
                ('language', models.ForeignKey(default=None, to='iati_codelists.Language', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('code', models.CharField(max_length=250, serialize=False, primary_key=True)),
                ('abbreviation', models.CharField(default=b'', max_length=120)),
                ('reported_by_organisation', models.CharField(default=b'', max_length=150)),
                ('name', models.CharField(default=b'', max_length=250)),
                ('original_ref', models.CharField(default=b'', max_length=120)),
                ('type', models.ForeignKey(default=None, to='iati_codelists.OrganisationType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OtherIdentifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_ref', models.CharField(default=b'', max_length=100)),
                ('owner_name', models.CharField(default=b'', max_length=100)),
                ('identifier', models.CharField(max_length=100)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('type', models.ForeignKey(to='iati_codelists.OtherIdentifierType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlannedDisbursement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.CharField(default=b'', max_length=100)),
                ('period_end', models.CharField(default=b'', max_length=100)),
                ('value_date', models.DateField(null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('updated', models.DateField(default=None, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('budget_type', models.ForeignKey(default=None, to='iati_codelists.BudgetType', null=True)),
                ('currency', models.ForeignKey(default=None, to='iati_codelists.Currency', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatedActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(default=b'', max_length=200)),
                ('text', models.TextField(default=b'')),
                ('current_activity', models.ForeignKey(related_name='current_activity', to='iati.Activity')),
                ('related_activity', models.ForeignKey(related_name='related_activity', on_delete=django.db.models.deletion.SET_NULL, to='iati.Activity', null=True)),
                ('type', models.ForeignKey(default=None, to='iati_codelists.RelatedActivityType', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aggregation_status', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('result_type', models.ForeignKey(default=None, to='iati_codelists.ResultType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=200)),
                ('description', models.TextField(default=b'')),
                ('baseline_year', models.IntegerField()),
                ('baseline_value', models.CharField(max_length=100)),
                ('comment', models.TextField(default=b'')),
                ('measure', models.ForeignKey(default=None, to='iati_codelists.IndicatorMeasure', null=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorBaseLineComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorMeasure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.CharField(default=b'', max_length=50)),
                ('period_end', models.CharField(default=b'', max_length=50)),
                ('planned_disbursement_period_start', models.CharField(default=b'', max_length=50)),
                ('planned_disbursement_period_end', models.CharField(default=b'', max_length=50)),
                ('target', models.CharField(default=b'', max_length=50)),
                ('actual', models.CharField(default=b'', max_length=50)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorPeriodActualComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator_period', models.ForeignKey(to='iati.ResultIndicatorPeriod')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorPeriodTargetComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator_period', models.ForeignKey(to='iati.ResultIndicatorPeriod')),
            ],
        ),
        migrations.CreateModel(
            name='ResultIndicatorTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
        ),
        migrations.CreateModel(
            name='ResultTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=None, null=True)),
                ('transaction_date', models.DateField(default=None, null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('ref', models.CharField(default=b'', max_length=255, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('aid_type', models.ForeignKey(default=None, to='iati_codelists.AidType', null=True)),
                ('currency', models.ForeignKey(default=None, to='iati_codelists.Currency', null=True)),
                ('description_type', models.ForeignKey(default=None, to='iati_codelists.DescriptionType', null=True)),
                ('disbursement_channel', models.ForeignKey(default=None, to='iati_codelists.DisbursementChannel', null=True)),
                ('finance_type', models.ForeignKey(default=None, to='iati_codelists.FinanceType', null=True)),
                ('flow_type', models.ForeignKey(default=None, to='iati_codelists.FlowType', null=True)),
                ('provider_activity', models.ForeignKey(related_name='transaction_provider_activity', db_constraint=False, to='iati.Activity', null=True)),
                ('provider_organisation', models.ForeignKey(related_name='transaction_provider_organisation', to='iati.Organisation', null=True)),
                ('receiver_activity', models.ForeignKey(related_name='transaction_receiver_activity', db_constraint=False, to='iati.Activity', null=True)),
                ('receiver_organisation', models.ForeignKey(related_name='transaction_receiver_organisation', to='iati.Organisation', null=True)),
                ('recipient_country', models.ForeignKey(default=None, to='geodata.Country', null=True)),
                ('recipient_region', models.ForeignKey(to='geodata.Region', null=True)),
                ('recipient_region_vocabulary', models.ForeignKey(default=1, to='iati_vocabulary.RegionVocabulary')),
                ('tied_status', models.ForeignKey(default=None, to='iati_codelists.TiedStatus', null=True)),
                ('transaction_type', models.ForeignKey(default=None, to='iati_codelists.TransactionType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction', models.ForeignKey(to='iati.Transaction')),
            ],
        ),
        migrations.AddField(
            model_name='budgetitem',
            name='country_budget_item',
            field=models.ForeignKey(to='iati.CountryBudgetItem'),
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, to='iati.Organisation', null=True),
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='role',
            field=models.ForeignKey(default=None, to='iati_codelists.OrganisationRole', null=True),
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='type',
            field=models.ForeignKey(default=None, to='iati_codelists.OrganisationType', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='participating_organisation',
            field=models.ManyToManyField(to='iati.Organisation', through='iati.ActivityParticipatingOrganisation'),
        ),
        migrations.AddField(
            model_name='activity',
            name='policy_marker',
            field=models.ManyToManyField(to='iati_codelists.PolicyMarker', through='iati.ActivityPolicyMarker'),
        ),
        migrations.AddField(
            model_name='activity',
            name='recipient_country',
            field=models.ManyToManyField(to='geodata.Country', through='iati.ActivityRecipientCountry'),
        ),
        migrations.AddField(
            model_name='activity',
            name='recipient_region',
            field=models.ManyToManyField(to='geodata.Region', through='iati.ActivityRecipientRegion'),
        ),
        migrations.AddField(
            model_name='activity',
            name='reporting_organisation',
            field=models.ForeignKey(related_name='activity_reporting_organisation', default=None, to='iati.Organisation', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='scope',
            field=models.ForeignKey(default=None, to='iati_codelists.ActivityScope', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='sector',
            field=models.ManyToManyField(to='iati_codelists.Sector', through='iati.ActivitySector'),
        ),
    ]
