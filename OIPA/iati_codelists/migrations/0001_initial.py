# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati_vocabulary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDateType',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='AidTypeFlag',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
            ],
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
        ),
        migrations.CreateModel(
            name='FinanceType',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=220)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FinanceTypeCategory',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FlowType',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='GeographicExactness',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='OtherFlags',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='PolicyMarker',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
                ('vocabulary', models.ForeignKey(default=None, to='iati_vocabulary.PolicyMarkerVocabulary', null=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('percentage', models.DecimalField(default=None, null=True, max_digits=5, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='SectorCategory',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
            ],
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
        ),
        migrations.CreateModel(
            name='ValueType',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default=b'')),
            ],
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
        ),
        migrations.AddField(
            model_name='sector',
            name='category',
            field=models.ForeignKey(default=None, to='iati_codelists.SectorCategory', null=True),
        ),
        migrations.AddField(
            model_name='sector',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati_vocabulary.SectorVocabulary', null=True),
        ),
        migrations.AddField(
            model_name='locationtype',
            name='category',
            field=models.ForeignKey(to='iati_codelists.LocationTypeCategory'),
        ),
        migrations.AddField(
            model_name='financetype',
            name='category',
            field=models.ForeignKey(to='iati_codelists.FinanceTypeCategory'),
        ),
        migrations.AddField(
            model_name='documentcategory',
            name='category',
            field=models.ForeignKey(to='iati_codelists.DocumentCategoryCategory'),
        ),
        migrations.AddField(
            model_name='budgetidentifiersector',
            name='category',
            field=models.ForeignKey(to='iati_codelists.BudgetIdentifierSectorCategory'),
        ),
        migrations.AddField(
            model_name='budgetidentifier',
            name='category',
            field=models.ForeignKey(to='iati_codelists.BudgetIdentifierSector'),
        ),
        migrations.AddField(
            model_name='budgetidentifier',
            name='vocabulary',
            field=models.ForeignKey(default=None, to='iati_vocabulary.BudgetIdentifierVocabulary', null=True),
        ),
        migrations.AddField(
            model_name='aidtype',
            name='category',
            field=models.ForeignKey(to='iati_codelists.AidTypeCategory'),
        ),
    ]
