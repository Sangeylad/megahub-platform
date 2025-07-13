# backend/ai_core/migrations/0001_initial.py

import ai_core.models.core_models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AIJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job_id', models.CharField(default=ai_core.models.core_models.generate_job_id, max_length=100, unique=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('running', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échoué'), ('cancelled', 'Annulé'), ('timeout', 'Timeout')], default='pending', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(choices=[('low', 'Basse'), ('normal', 'Normale'), ('high', 'Haute'), ('urgent', 'Urgente')], default='normal', max_length=20)),
                ('input_data', models.JSONField(default=dict)),
                ('result_data', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('progress_percentage', models.IntegerField(default=0)),
                ('task_id', models.CharField(blank=True, max_length=100)),
                ('is_async', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ai_job',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIJobType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('chat', 'Chat Completion'), ('assistant', 'Assistant'), ('upload', 'File Upload'), ('analysis', 'Analysis'), ('generation', 'Content Generation')], max_length=50)),
                ('estimated_duration_seconds', models.IntegerField(default=30)),
                ('requires_async', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ai_job_type',
                'ordering': ['category', 'name'],
            },
        ),
    ]
