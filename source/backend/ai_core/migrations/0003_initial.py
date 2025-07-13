# backend/ai_core/migrations/0003_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_core', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='aijob',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_jobs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='aijob',
            name='job_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_core.aijobtype'),
        ),
        migrations.AddIndex(
            model_name='aijob',
            index=models.Index(fields=['status', 'created_at'], name='ai_job_status_ba4967_idx'),
        ),
        migrations.AddIndex(
            model_name='aijob',
            index=models.Index(fields=['brand', 'status'], name='ai_job_brand_i_f1c042_idx'),
        ),
        migrations.AddIndex(
            model_name='aijob',
            index=models.Index(fields=['job_id'], name='ai_job_job_id_c236e5_idx'),
        ),
    ]
