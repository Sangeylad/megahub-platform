# backend/task_core/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basetask',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='basetask',
            index=models.Index(fields=['task_type', 'status'], name='task_base_task_ty_fc6ccd_idx'),
        ),
        migrations.AddIndex(
            model_name='basetask',
            index=models.Index(fields=['brand', 'status'], name='task_base_brand_i_7e05a7_idx'),
        ),
        migrations.AddIndex(
            model_name='basetask',
            index=models.Index(fields=['celery_task_id'], name='task_base_celery__8a5207_idx'),
        ),
        migrations.AddIndex(
            model_name='basetask',
            index=models.Index(fields=['priority', 'status'], name='task_base_priorit_33c4f8_idx'),
        ),
    ]
