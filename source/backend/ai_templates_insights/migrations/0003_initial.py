# backend/ai_templates_insights/migrations/0003_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ai_templates_insights', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templaterecommendation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templateinsight',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insights', to='ai_templates_core.basetemplate'),
        ),
        migrations.AddField(
            model_name='optimizationsuggestion',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='optimization_suggestions', to='ai_templates_core.basetemplate'),
        ),
        migrations.AddIndex(
            model_name='templaterecommendation',
            index=models.Index(fields=['brand', 'is_active', 'priority'], name='template_re_brand_i_98a39f_idx'),
        ),
        migrations.AddIndex(
            model_name='templaterecommendation',
            index=models.Index(fields=['user', 'recommendation_type'], name='template_re_user_id_c511f7_idx'),
        ),
        migrations.AddIndex(
            model_name='templateinsight',
            index=models.Index(fields=['template', 'is_resolved'], name='template_in_templat_6d3c69_idx'),
        ),
        migrations.AddIndex(
            model_name='templateinsight',
            index=models.Index(fields=['insight_type', 'severity'], name='template_in_insight_f267ab_idx'),
        ),
        migrations.AddIndex(
            model_name='optimizationsuggestion',
            index=models.Index(fields=['template', 'is_implemented'], name='optimizatio_templat_115cbe_idx'),
        ),
        migrations.AddIndex(
            model_name='optimizationsuggestion',
            index=models.Index(fields=['suggestion_type', 'estimated_impact'], name='optimizatio_suggest_abffab_idx'),
        ),
    ]
