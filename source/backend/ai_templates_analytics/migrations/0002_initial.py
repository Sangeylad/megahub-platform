# backend/ai_templates_analytics/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_analytics', '0001_initial'),
        ('ai_templates_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templateusagemetrics',
            name='template',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='usage_metrics', to='ai_templates_core.basetemplate'),
        ),
    ]
