# backend/ai_usage/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_core', '0002_initial'),
        ('ai_usage', '0001_initial'),
        ('company_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiusagealert',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company_core.company'),
        ),
        migrations.AddField(
            model_name='aijobusage',
            name='ai_job',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='usage', to='ai_core.aijob'),
        ),
        migrations.AddIndex(
            model_name='aijobusage',
            index=models.Index(fields=['provider_name', 'created_at'], name='ai_job_usag_provide_1b1cfc_idx'),
        ),
        migrations.AddIndex(
            model_name='aijobusage',
            index=models.Index(fields=['ai_job', 'created_at'], name='ai_job_usag_ai_job__52e66d_idx'),
        ),
    ]
