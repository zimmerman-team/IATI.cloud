# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0001_initial'),
    ]

    operations = [
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
        migrations.RenameField(
            model_name='budgetitem',
            old_name='counry_budget_item',
            new_name='country_budget_item',
        ),
    ]
