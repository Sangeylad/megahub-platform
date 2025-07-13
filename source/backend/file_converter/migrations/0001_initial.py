# backend/file_converter/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversionQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_limit', models.PositiveIntegerField(default=100)),
                ('current_month_usage', models.PositiveIntegerField(default=0)),
                ('max_file_size', models.PositiveIntegerField(default=52428800)),
                ('reset_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'file_converter_quota',
            },
        ),
        migrations.CreateModel(
            name='SupportedFormat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('mime_type', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('document', 'Document'), ('image', 'Image'), ('presentation', 'Présentation'), ('spreadsheet', 'Tableur')], max_length=20)),
                ('is_input', models.BooleanField(default=True)),
                ('is_output', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'file_converter_supported_format',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FileConversion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_filename', models.CharField(max_length=255)),
                ('original_size', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échec')], default='pending', max_length=20)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('output_filename', models.CharField(blank=True, max_length=255)),
                ('output_size', models.PositiveIntegerField(blank=True, null=True)),
                ('download_url', models.URLField(blank=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('conversion_time', models.FloatField(blank=True, null=True)),
                ('task_id', models.CharField(blank=True, max_length=255)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('input_format', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_conversions', to='file_converter.supportedformat')),
                ('output_format', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='output_conversions', to='file_converter.supportedformat')),
            ],
            options={
                'db_table': 'file_converter_conversion',
                'ordering': ['-created_at'],
            },
        ),
    ]
