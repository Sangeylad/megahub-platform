# backend/public_tools/migrations/0001_initial.py

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PublicCompressionQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('hourly_usage', models.PositiveIntegerField(default=0)),
                ('daily_usage', models.PositiveIntegerField(default=0)),
                ('last_compression', models.DateTimeField(auto_now=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('block_reason', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_compression_quota',
            },
        ),
        migrations.CreateModel(
            name='PublicConversionQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('hourly_usage', models.PositiveIntegerField(default=0)),
                ('daily_usage', models.PositiveIntegerField(default=0)),
                ('last_conversion', models.DateTimeField(auto_now=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('block_reason', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_conversion_quota',
            },
        ),
        migrations.CreateModel(
            name='PublicOptimizationQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('hourly_usage', models.PositiveIntegerField(default=0)),
                ('daily_usage', models.PositiveIntegerField(default=0)),
                ('last_optimization', models.DateTimeField(auto_now=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('block_reason', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_optimization_quota',
            },
        ),
        migrations.CreateModel(
            name='ToolUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tool_name', models.CharField(max_length=50)),
                ('ip_address', models.GenericIPAddressField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'public_tools_usage',
            },
        ),
        migrations.CreateModel(
            name='PublicFileOptimization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_filename', models.CharField(max_length=255)),
                ('original_size', models.PositiveBigIntegerField()),
                ('original_mime_type', models.CharField(max_length=100)),
                ('file_extension', models.CharField(max_length=10)),
                ('quality_level', models.CharField(choices=[('low', 'Basse qualité (compression max)'), ('medium', 'Qualité moyenne'), ('high', 'Haute qualité (compression légère)')], default='medium', max_length=20)),
                ('resize_enabled', models.BooleanField(default=False)),
                ('target_max_dimension', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échec')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('optimized_filename', models.CharField(blank=True, max_length=255)),
                ('optimized_size', models.PositiveBigIntegerField(blank=True, null=True)),
                ('compression_ratio', models.FloatField(blank=True, null=True)),
                ('size_reduction_bytes', models.PositiveBigIntegerField(blank=True, null=True)),
                ('size_reduction_percentage', models.FloatField(blank=True, null=True)),
                ('download_token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('optimization_time', models.FloatField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('task_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_file_optimization',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['ip_address', '-created_at'], name='public_tool_ip_addr_6cbd14_idx'), models.Index(fields=['status', 'created_at'], name='public_tool_status_e6c035_idx'), models.Index(fields=['expires_at'], name='public_tool_expires_bb9e28_idx'), models.Index(fields=['download_token'], name='public_tool_downloa_b21ff8_idx')],
            },
        ),
        migrations.CreateModel(
            name='PublicFileConversion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_filename', models.CharField(max_length=255)),
                ('original_size', models.PositiveIntegerField()),
                ('input_format', models.CharField(max_length=10)),
                ('output_format', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échec')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('output_filename', models.CharField(blank=True, max_length=255)),
                ('output_size', models.PositiveIntegerField(blank=True, null=True)),
                ('download_token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('conversion_time', models.FloatField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('task_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_file_conversion',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['ip_address', '-created_at'], name='public_tool_ip_addr_ba4d6f_idx'), models.Index(fields=['status', 'created_at'], name='public_tool_status_baca03_idx'), models.Index(fields=['expires_at'], name='public_tool_expires_09d4af_idx'), models.Index(fields=['download_token'], name='public_tool_downloa_3acf12_idx')],
            },
        ),
        migrations.CreateModel(
            name='PublicFileCompression',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('source_files_info', models.JSONField(default=list)),
                ('total_source_size', models.PositiveBigIntegerField()),
                ('files_count', models.PositiveIntegerField()),
                ('output_format', models.CharField(default='zip', max_length=10)),
                ('compression_level', models.CharField(choices=[('fastest', 'Rapide'), ('normal', 'Normal'), ('maximum', 'Maximum')], default='normal', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échec')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('archive_filename', models.CharField(blank=True, max_length=255)),
                ('archive_size', models.PositiveBigIntegerField(blank=True, null=True)),
                ('compression_ratio', models.FloatField(blank=True, null=True)),
                ('download_token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('compression_time', models.FloatField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('task_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'public_tools_file_compression',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['ip_address', '-created_at'], name='public_tool_ip_addr_7a23f2_idx'), models.Index(fields=['status', 'created_at'], name='public_tool_status_c7f0f7_idx'), models.Index(fields=['expires_at'], name='public_tool_expires_35c7d1_idx'), models.Index(fields=['download_token'], name='public_tool_downloa_ac28e3_idx')],
            },
        ),
    ]
