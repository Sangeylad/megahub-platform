# backend/file_compressor/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file_compressor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileoptimization',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='fileoptimization',
            index=models.Index(fields=['user', 'brand', '-created_at'], name='file_compre_user_id_f4b691_idx'),
        ),
        migrations.AddIndex(
            model_name='fileoptimization',
            index=models.Index(fields=['status', 'created_at'], name='file_compre_status_127265_idx'),
        ),
        migrations.AddIndex(
            model_name='fileoptimization',
            index=models.Index(fields=['expires_at'], name='file_compre_expires_c7713b_idx'),
        ),
        migrations.AddIndex(
            model_name='fileoptimization',
            index=models.Index(fields=['file_type', 'status'], name='file_compre_file_ty_86828d_idx'),
        ),
    ]
