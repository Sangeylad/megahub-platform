# backend/ai_templates_analytics/migrations/0003_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_categories', '0001_initial'),
        ('ai_templates_analytics', '0002_initial'),
        ('brands_core', '0001_initial'),
        ('ai_templates_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatepopularity',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand'),
        ),
        migrations.AddField(
            model_name='templatepopularity',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ai_templates_categories.templatecategory'),
        ),
        migrations.AddField(
            model_name='templatepopularity',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='popularity_rankings', to='ai_templates_core.basetemplate'),
        ),
        migrations.AddField(
            model_name='templateperformance',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_logs', to='ai_templates_core.basetemplate'),
        ),
    ]
