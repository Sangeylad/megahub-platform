# backend/ai_openai/migrations/0001_initial.py

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenAIConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('base_url', models.URLField(default='https://api.openai.com')),
                ('timeout_seconds', models.IntegerField(default=300)),
                ('max_retries', models.IntegerField(default=3)),
                ('available_models', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'openai_config',
            },
        ),
        migrations.CreateModel(
            name='OpenAIJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('model', models.CharField(default='gpt-4o', max_length=50)),
                ('temperature', models.FloatField(blank=True, help_text='Temperature entre 0.0 et 2.0. NULL pour O3.', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(2.0)])),
                ('max_tokens', models.IntegerField(blank=True, null=True)),
                ('reasoning_effort', models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], help_text='Effort de raisonnement pour O3', max_length=10, null=True)),
                ('max_completion_tokens', models.IntegerField(blank=True, null=True)),
                ('messages', models.JSONField(default=list)),
                ('messages_format', models.CharField(choices=[('legacy', 'Legacy'), ('structured', 'Structured')], default='legacy', max_length=20)),
                ('tools', models.JSONField(blank=True, default=list)),
                ('tool_resources', models.JSONField(blank=True, default=dict)),
                ('response_format', models.JSONField(blank=True, default=dict)),
                ('openai_id', models.CharField(blank=True, max_length=100)),
                ('completion_tokens', models.IntegerField(default=0)),
                ('prompt_tokens', models.IntegerField(default=0)),
                ('total_tokens', models.IntegerField(default=0)),
                ('assistant_id', models.CharField(blank=True, max_length=100)),
                ('thread_id', models.CharField(blank=True, max_length=100)),
                ('run_id', models.CharField(blank=True, max_length=100)),
                ('ai_job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='openai_job', to='ai_core.aijob')),
            ],
            options={
                'db_table': 'openai_job',
                'ordering': ['-created_at'],
            },
        ),
    ]
