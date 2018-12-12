# XXX: This migration is manually created, because this particular relationship
# got lost when migrations were merged

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0047_merge_20181009_1130'),
    ]

    operations = [
        # migrations.AddField(
            # model_name='location',
            # name='result_indicator_baseline',
            # field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='baseline_locations', to='iati.ResultIndicator'),
        # ),
    ]
