# backend/file_compressor/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportedFileType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('extension', models.CharField(max_length=10)),
                ('mime_type', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('document', 'Document'), ('image', 'Image'), ('video', 'Vidéo'), ('audio', 'Audio')], max_length=20)),
                ('average_compression_ratio', models.FloatField(default=0.5)),
                ('is_active', models.BooleanField(default=True)),
                ('max_file_size', models.PositiveIntegerField(default=52428800)),
                ('supports_quality_levels', models.BooleanField(default=True)),
                ('supports_resize', models.BooleanField(default=False)),
                ('default_quality', models.PositiveSmallIntegerField(default=75)),
            ],
            options={
                'db_table': 'file_compressor_supported_type',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='OptimizationQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_limit', models.PositiveIntegerField(default=100)),
                ('current_month_usage', models.PositiveIntegerField(default=0)),
                ('max_file_size', models.PositiveBigIntegerField(default=52428800)),
                ('reset_date', models.DateTimeField()),
                ('can_use_lossless', models.BooleanField(default=False)),
                ('can_resize', models.BooleanField(default=True)),
                ('can_custom_quality', models.BooleanField(default=True)),
                ('max_resolution', models.PositiveIntegerField(default=1920)),
                ('brand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
            ],
            options={
                'db_table': 'file_compressor_quota',
            },
        ),
        migrations.CreateModel(
            name='FileOptimization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_filename', models.CharField(max_length=255)),
                ('original_size', models.PositiveBigIntegerField()),
                ('original_mime_type', models.CharField(max_length=100)),
                ('quality_level', models.CharField(choices=[('low', 'Basse qualité (compression max)'), ('medium', 'Qualité moyenne'), ('high', 'Haute qualité (compression légère)'), ('lossless', 'Sans perte (si supporté)')], default='medium', max_length=20)),
                ('custom_quality', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('resize_enabled', models.BooleanField(default=False)),
                ('target_width', models.PositiveIntegerField(blank=True, null=True)),
                ('target_height', models.PositiveIntegerField(blank=True, null=True)),
                ('maintain_aspect_ratio', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échec')], default='pending', max_length=20)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('optimized_filename', models.CharField(blank=True, max_length=255)),
                ('optimized_size', models.PositiveBigIntegerField(blank=True, null=True)),
                ('compression_ratio', models.FloatField(blank=True, null=True)),
                ('size_reduction_bytes', models.PositiveBigIntegerField(blank=True, null=True)),
                ('size_reduction_percentage', models.FloatField(blank=True, null=True)),
                ('download_url', models.URLField(blank=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('optimization_time', models.FloatField(blank=True, null=True)),
                ('task_id', models.CharField(blank=True, max_length=255)),
                ('final_dimensions', models.JSONField(blank=True, null=True)),
                ('final_quality', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('optimization_details', models.JSONField(blank=True, null=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('file_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_compressor.supportedfiletype')),
            ],
            options={
                'db_table': 'file_compressor_optimization',
                'ordering': ['-created_at'],
            },
        ),
    ]
