# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('geodata', '__first__'),
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
                ('start_planned', models.DateField(default=None, null=True, blank=True)),
                ('end_planned', models.DateField(default=None, null=True, blank=True)),
                ('start_actual', models.DateField(default=None, null=True, blank=True)),
                ('end_actual', models.DateField(default=None, null=True, blank=True)),
                ('xml_source_ref', models.CharField(default=b'', max_length=200)),
                ('total_budget', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, db_index=True)),
                ('capital_spend', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('has_conditions', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_date', models.DateField(null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityDateType',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityParticipatingOrganisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default=b'')),
                ('activity', models.ForeignKey(related_name='participating_organisations', to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityPolicyMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alt_policy_marker', models.CharField(default=b'', max_length=200)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityRecipientCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('country', models.ForeignKey(to='geodata.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityRecipientRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('region', models.ForeignKey(to='geodata.Region')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityScope',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivitySector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alt_sector_name', models.CharField(default=b'', max_length=200)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityStatus',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityWebsite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AidType',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AidTypeCategory',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AidTypeFlag',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetIdentifier',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetIdentifierSector',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetIdentifierSectorCategory',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetIdentifierVocabulary',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'', max_length=50)),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetItemDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget_item', models.ForeignKey(to='iati.BudgetItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CollaborationType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConditionType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person_name', models.CharField(default=b'', max_length=100)),
                ('organisation', models.CharField(default=b'', max_length=100)),
                ('telephone', models.CharField(default=b'', max_length=100)),
                ('email', models.TextField(default=b'')),
                ('mailing_address', models.TextField(default=b'')),
                ('website', models.CharField(default=b'', max_length=255)),
                ('job_title', models.CharField(default=b'', max_length=150)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfoDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfoJobTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfoMailingAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfoOrganisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfoPersonName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ContactInfo', models.ForeignKey(to='iati.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
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
                ('vocabulary', models.ForeignKey(to='iati.BudgetIdentifierVocabulary', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrsAdd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
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
            ],
            options={
            },
            bases=(models.Model,),
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrsAddOtherFlags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('other_flags_significance', models.IntegerField(default=None, null=True)),
                ('crs_add', models.ForeignKey(to='iati.CrsAdd')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=b'')),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DisbursementChannel',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.TextField(default=b'')),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentCategoryCategory',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(max_length=500)),
                ('title', models.CharField(default=b'', max_length=255)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('document_category', models.ForeignKey(default=None, to='iati.DocumentCategory', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentLinkTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_link', models.ForeignKey(to='iati.DocumentLink')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ffs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extraction_date', models.DateField(default=None, null=True)),
                ('priority', models.BooleanField(default=False)),
                ('phaseout_year', models.IntegerField(max_length=4, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FfsForecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(max_length=4, null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('currency', models.ForeignKey(to='iati.Currency')),
                ('ffs', models.ForeignKey(to='iati.Ffs')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('category', models.CharField(default=b'', max_length=100)),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FinanceType',
            fields=[
                ('code', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=220)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FinanceTypeCategory',
            fields=[
                ('code', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowType',
            fields=[
                ('code', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GazetteerAgency',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicalPrecision',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicExactness',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('category', models.CharField(max_length=50)),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicLocationClass',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicLocationReach',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicVocabulary',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default=b'')),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndicatorMeasure',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LegacyData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, null=True)),
                ('value', models.CharField(max_length=200, null=True)),
                ('iati_equivalent', models.CharField(max_length=20, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoanRepaymentPeriod',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoanRepaymentType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(default=b'', max_length=200)),
                ('name', models.TextField(default=b'', max_length=1000)),
                ('type_description', models.CharField(default=b'', max_length=200)),
                ('description', models.TextField(default=b'')),
                ('activity_description', models.TextField(default=b'')),
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
                ('adm_vocabulary', models.ForeignKey(related_name='administrative_vocabulary', default=None, to='iati.GeographicVocabulary', null=True)),
                ('description_type', models.ForeignKey(default=None, to='iati.DescriptionType', null=True)),
                ('exactness', models.ForeignKey(default=None, to='iati.GeographicExactness', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationActivityDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='iati.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationTypeCategory',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Narrative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.CharField(max_length=50, null=True, verbose_name=b'related object')),
                ('iati_identifier', models.CharField(max_length=50, null=True, verbose_name=b'iati_identifier')),
                ('content', models.TextField()),
                ('content_type', models.ForeignKey(verbose_name=b'xml Parent', blank=True, to='contenttypes.ContentType', null=True)),
                ('language', models.ForeignKey(default=None, to='iati.Language', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('code', models.CharField(max_length=80, serialize=False, primary_key=True)),
                ('abbreviation', models.CharField(default=b'', max_length=80)),
                ('reported_by_organisation', models.CharField(default=b'', max_length=100)),
                ('name', models.CharField(default=b'', max_length=250)),
                ('original_ref', models.CharField(default=b'', max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganisationIdentifier',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('abbreviation', models.CharField(default=None, max_length=30, null=True)),
                ('name', models.CharField(default=None, max_length=250, null=True)),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganisationRegistrationAgency',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('category', models.CharField(max_length=2)),
                ('url', models.URLField(default=b'')),
                ('public_database', models.BooleanField(default=False)),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganisationRole',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganisationType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherFlags',
            fields=[
                ('code', models.IntegerField(max_length=4, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherIdentifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_ref', models.CharField(default=b'', max_length=100)),
                ('owner_name', models.CharField(default=b'', max_length=100)),
                ('identifier', models.CharField(max_length=100)),
                ('activity', models.ForeignKey(to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherIdentifierType',
            fields=[
                ('code', models.CharField(default=b'', max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
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
                ('budget_type', models.ForeignKey(default=None, to='iati.BudgetType', null=True)),
                ('currency', models.ForeignKey(default=None, to='iati.Currency', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolicyMarker',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolicyMarkerVocabulary',
            fields=[
                ('code', models.IntegerField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolicySignificance',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublisherType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegionVocabulary',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelatedActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(default=b'', max_length=200)),
                ('text', models.TextField(default=b'')),
                ('current_activity', models.ForeignKey(related_name='current_activity', to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelatedActivityType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255)),
                ('description', models.TextField(default=b'')),
                ('aggregation_status', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(related_name='results', to='iati.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=200)),
                ('description', models.TextField(default=b'')),
                ('baseline_year', models.IntegerField(max_length=4)),
                ('baseline_value', models.CharField(max_length=100)),
                ('comment', models.TextField(default=b'')),
                ('measure', models.ForeignKey(default=None, to='iati.IndicatorMeasure', null=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicatorBaseLineComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicatorDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
            options={
            },
            bases=(models.Model,),
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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicatorPeriodActualComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator_period', models.ForeignKey(to='iati.ResultIndicatorPeriod')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicatorPeriodTargetComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator_period', models.ForeignKey(to='iati.ResultIndicatorPeriod')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultIndicatorTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_indicator', models.ForeignKey(to='iati.ResultIndicator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.ForeignKey(to='iati.Result')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultType',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectorCategory',
            fields=[
                ('code', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectorVocabulary',
            fields=[
                ('code', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TiedStatus',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, db_index=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('language', models.ForeignKey(default=None, to='iati.Language', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=None, null=True)),
                ('provider_organisation_name', models.CharField(default=b'', max_length=255)),
                ('provider_activity', models.CharField(max_length=100, null=True)),
                ('receiver_organisation_name', models.CharField(default=b'', max_length=255)),
                ('transaction_date', models.DateField(default=None, null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('ref', models.CharField(default=b'', max_length=255, null=True)),
                ('activity', models.ForeignKey(to='iati.Activity')),
                ('aid_type', models.ForeignKey(default=None, to='iati.AidType', null=True)),
                ('currency', models.ForeignKey(default=None, to='iati.Currency', null=True)),
                ('description_type', models.ForeignKey(default=None, to='iati.DescriptionType', null=True)),
                ('disbursement_channel', models.ForeignKey(default=None, to='iati.DisbursementChannel', null=True)),
                ('finance_type', models.ForeignKey(default=None, to='iati.FinanceType', null=True)),
                ('flow_type', models.ForeignKey(default=None, to='iati.FlowType', null=True)),
                ('provider_organisation', models.ForeignKey(related_name='transaction_providing_organisation_old', default=None, to='iati.Organisation', null=True)),
                ('receiver_organisation', models.ForeignKey(related_name='transaction_receiving_organisation_old', default=None, to='iati.Organisation', null=True)),
                ('recipient_country', models.ForeignKey(default=None, to='geodata.Country', null=True)),
                ('recipient_region', models.ForeignKey(to='geodata.Region', null=True)),
                ('recipient_region_vocabulary', models.ForeignKey(default=1, to='iati.RegionVocabulary')),
                ('tied_status', models.ForeignKey(default=None, to='iati.TiedStatus', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction', models.ForeignKey(to='iati.Transaction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255)),
                ('organisation', models.ForeignKey(related_name='transaction_providing_organisation', default=None, to='iati.Organisation', null=True)),
                ('transaction', models.ForeignKey(to='iati.Transaction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionReciever',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255)),
                ('organisation', models.ForeignKey(related_name='transaction_recieving_organisation', default=None, to='iati.Organisation', null=True)),
                ('transaction', models.ForeignKey(to='iati.Transaction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionSector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector', models.ForeignKey(to='iati.Sector')),
                ('transaction', models.ForeignKey(to='iati.Transaction')),
                ('vocabulary', models.ForeignKey(to='iati.SectorVocabulary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ValueType',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerificationStatus',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('code', models.CharField(default=b'', max_length=4, serialize=False, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('description', models.TextField(default=b'')),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=140)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.ForeignKey(default=None, to='iati.TransactionType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sector',
            name='category',
            field=models.ForeignKey(default=None, to='iati.SectorCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sector',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati.SectorVocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='result',
            name='result_type',
            field=models.ForeignKey(default=None, to='iati.ResultType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relatedactivity',
            name='type',
            field=models.ForeignKey(default=None, to='iati.RelatedActivityType', max_length=200, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policymarker',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati.PolicyMarkerVocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='otheridentifier',
            name='type',
            field=models.ForeignKey(to='iati.OtherIdentifierType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organisation',
            name='type',
            field=models.ForeignKey(default=None, to='iati.OrganisationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationtype',
            name='category',
            field=models.ForeignKey(to='iati.LocationTypeCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='feature_designation',
            field=models.ForeignKey(related_name='feature_designation', default=None, to='iati.LocationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='gazetteer_ref',
            field=models.ForeignKey(default=None, to='iati.GazetteerAgency', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='location_class',
            field=models.ForeignKey(default=None, to='iati.GeographicLocationClass', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='location_id_vocabulary',
            field=models.ForeignKey(related_name='location_id_vocabulary', default=None, to='iati.GeographicVocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='location_reach',
            field=models.ForeignKey(default=None, to='iati.GeographicLocationReach', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='precision',
            field=models.ForeignKey(default=None, to='iati.GeographicalPrecision', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='type',
            field=models.ForeignKey(related_name='deprecated_location_type', default=None, to='iati.LocationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='financetype',
            name='category',
            field=models.ForeignKey(to='iati.FinanceTypeCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documentlink',
            name='file_format',
            field=models.ForeignKey(default=None, to='iati.FileFormat', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documentlink',
            name='language',
            field=models.ForeignKey(default=None, to='iati.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documentcategory',
            name='category',
            field=models.ForeignKey(to='iati.DocumentCategoryCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='description',
            name='type',
            field=models.ForeignKey(related_name='description_type', default=None, to='iati.DescriptionType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crsaddotherflags',
            name='other_flags',
            field=models.ForeignKey(to='iati.OtherFlags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crsaddloanterms',
            name='repayment_plan',
            field=models.ForeignKey(default=None, to='iati.LoanRepaymentPeriod', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crsaddloanterms',
            name='repayment_type',
            field=models.ForeignKey(default=None, to='iati.LoanRepaymentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crsaddloanstatus',
            name='currency',
            field=models.ForeignKey(default=None, to='iati.Currency', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='contact_type',
            field=models.ForeignKey(default=None, to='iati.ContactType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condition',
            name='type',
            field=models.ForeignKey(default=None, to='iati.ConditionType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetitem',
            name='country_budget_item',
            field=models.ForeignKey(to='iati.CountryBudgetItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetidentifiersector',
            name='category',
            field=models.ForeignKey(to='iati.BudgetIdentifierSectorCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetidentifier',
            name='category',
            field=models.ForeignKey(to='iati.BudgetIdentifierSector'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetidentifier',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati.BudgetIdentifierVocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budget',
            name='currency',
            field=models.ForeignKey(default=None, to='iati.Currency', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budget',
            name='type',
            field=models.ForeignKey(default=None, to='iati.BudgetType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aidtype',
            name='category',
            field=models.ForeignKey(to='iati.AidTypeCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitysector',
            name='sector',
            field=models.ForeignKey(default=None, to='iati.Sector', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitysector',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati.Vocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityrecipientregion',
            name='region_vocabulary',
            field=models.ForeignKey(default=1, to='iati.RegionVocabulary'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitypolicymarker',
            name='policy_marker',
            field=models.ForeignKey(related_name='policy_marker_related', default=None, to='iati.PolicyMarker', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitypolicymarker',
            name='policy_significance',
            field=models.ForeignKey(default=None, to='iati.PolicySignificance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitypolicymarker',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati.Vocabulary', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, to='iati.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='role',
            field=models.ForeignKey(default=None, to='iati.OrganisationRole', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='type',
            field=models.ForeignKey(default=None, to='iati.OrganisationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitydate',
            name='type',
            field=models.ForeignKey(to='iati.ActivityDateType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='activity_status',
            field=models.ForeignKey(default=None, to='iati.ActivityStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='collaboration_type',
            field=models.ForeignKey(default=None, to='iati.CollaborationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='default_aid_type',
            field=models.ForeignKey(default=None, to='iati.AidType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='default_currency',
            field=models.ForeignKey(related_name='default_currency', default=None, to='iati.Currency', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='default_finance_type',
            field=models.ForeignKey(default=None, to='iati.FinanceType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='default_flow_type',
            field=models.ForeignKey(default=None, to='iati.FlowType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='default_tied_status',
            field=models.ForeignKey(default=None, to='iati.TiedStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='iati_standard_version',
            field=models.ForeignKey(to='iati.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='participating_organisation',
            field=models.ManyToManyField(to='iati.Organisation', through='iati.ActivityParticipatingOrganisation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='policy_marker',
            field=models.ManyToManyField(to='iati.PolicyMarker', through='iati.ActivityPolicyMarker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='recipient_country',
            field=models.ManyToManyField(to='geodata.Country', through='iati.ActivityRecipientCountry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='recipient_region',
            field=models.ManyToManyField(to='geodata.Region', through='iati.ActivityRecipientRegion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='reporting_organisation',
            field=models.ForeignKey(related_name='activity_reporting_organisation', default=None, to='iati.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='scope',
            field=models.ForeignKey(default=None, to='iati.ActivityScope', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='sector',
            field=models.ManyToManyField(to='iati.Sector', through='iati.ActivitySector'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='total_budget_currency',
            field=models.ForeignKey(related_name='total_budget_currency', default=None, to='iati.Currency', null=True),
            preserve_default=True,
        ),
    ]
