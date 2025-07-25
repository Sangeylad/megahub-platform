# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('brands_core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('integration_type', models.CharField(choices=[('crm', 'CRM'), ('ecommerce', 'E-commerce'), ('webhook', 'Webhook'), ('api', 'API'), ('zapier', 'Zapier'), ('wordpress', 'WordPress'), ('landing_page', 'Landing Page'), ('form_builder', 'Form Builder')], max_length=30)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('error', 'Error'), ('pending', 'Pending')], default='active', max_length=20)),
                ('configuration', models.JSONField(default=dict)),
                ('api_endpoint', models.URLField(blank=True)),
                ('api_key', models.CharField(blank=True, max_length=255)),
                ('webhook_url', models.URLField(blank=True)),
                ('sync_frequency', models.CharField(default='real_time', max_length=20)),
                ('last_sync', models.DateTimeField(blank=True, null=True)),
                ('sync_status', models.CharField(default='pending', max_length=20)),
                ('error_log', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IntegrationLog',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=20)),
                ('request_data', models.JSONField(default=dict)),
                ('response_data', models.JSONField(default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('execution_time_ms', models.IntegerField(default=0)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='mailing_integrations_core.integration')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
