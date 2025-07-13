# backend/seo_pages_workflow/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seo_pages_workflow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageworkflowhistory',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pageworkflowhistory',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_history', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='pagestatus',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_status', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='pagestatus',
            name='status_changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagescheduling',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='scheduling', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='pagescheduling',
            name='scheduled_by',
            field=models.ForeignKey(blank=True, help_text='Utilisateur ayant programmé la publication', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scheduled_pages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='pagestatus',
            index=models.Index(fields=['status'], name='seo_pages_w_status_a7b844_idx'),
        ),
        migrations.AddIndex(
            model_name='pagestatus',
            index=models.Index(fields=['status_changed_at'], name='seo_pages_w_status__b2f2df_idx'),
        ),
        migrations.AddIndex(
            model_name='pagescheduling',
            index=models.Index(fields=['scheduled_publish_date', 'auto_publish'], name='seo_pages_w_schedul_8cf7e7_idx'),
        ),
    ]
