# backend/file_converter/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file_converter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileconversion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversionquota',
            name='brand',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand'),
        ),
        migrations.AddIndex(
            model_name='fileconversion',
            index=models.Index(fields=['user', 'brand', '-created_at'], name='file_conver_user_id_40ef09_idx'),
        ),
        migrations.AddIndex(
            model_name='fileconversion',
            index=models.Index(fields=['status', 'created_at'], name='file_conver_status_f5fd58_idx'),
        ),
        migrations.AddIndex(
            model_name='fileconversion',
            index=models.Index(fields=['expires_at'], name='file_conver_expires_8c085c_idx'),
        ),
    ]
