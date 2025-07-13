# backend/ai_providers/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AICredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('openai_api_key', models.TextField(blank=True)),
                ('anthropic_api_key', models.TextField(blank=True)),
                ('google_api_key', models.TextField(blank=True)),
                ('use_global_fallback', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ai_credentials',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('base_url', models.URLField()),
                ('supports_chat', models.BooleanField(default=True)),
                ('supports_assistants', models.BooleanField(default=False)),
                ('supports_files', models.BooleanField(default=False)),
                ('supports_vision', models.BooleanField(default=False)),
                ('default_model', models.CharField(max_length=100)),
                ('available_models', models.JSONField(default=list)),
                ('rate_limit_rpm', models.IntegerField(default=60)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'ai_provider',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('monthly_token_limit', models.IntegerField(default=1000000)),
                ('monthly_cost_limit', models.DecimalField(decimal_places=2, default=100.0, max_digits=10)),
                ('current_tokens_used', models.IntegerField(default=0)),
                ('current_cost_used', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('last_reset_date', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ai_quota',
            },
        ),
    ]
