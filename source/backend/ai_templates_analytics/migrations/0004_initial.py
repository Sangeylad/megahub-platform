# backend/ai_templates_analytics/migrations/0004_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0002_initial'),
        ('ai_templates_analytics', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='templateperformance',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templatefeedback',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='ai_templates_core.basetemplate'),
        ),
        migrations.AddField(
            model_name='templatefeedback',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='templatepopularity',
            index=models.Index(fields=['brand', 'ranking_period', 'period_start'], name='template_po_brand_i_8f2ab7_idx'),
        ),
        migrations.AddIndex(
            model_name='templatepopularity',
            index=models.Index(fields=['category', 'ranking_period'], name='template_po_categor_ffea29_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='templatepopularity',
            unique_together={('template', 'ranking_period', 'period_start', 'brand')},
        ),
        migrations.AddIndex(
            model_name='templateperformance',
            index=models.Index(fields=['template', 'was_successful'], name='template_pe_templat_6feb49_idx'),
        ),
        migrations.AddIndex(
            model_name='templateperformance',
            index=models.Index(fields=['user', 'created_at'], name='template_pe_user_id_484d04_idx'),
        ),
        migrations.AddIndex(
            model_name='templatefeedback',
            index=models.Index(fields=['template', 'rating'], name='template_fe_templat_f5ada5_idx'),
        ),
        migrations.AddIndex(
            model_name='templatefeedback',
            index=models.Index(fields=['feedback_type', 'is_public'], name='template_fe_feedbac_7045bd_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='templatefeedback',
            unique_together={('template', 'user')},
        ),
    ]
