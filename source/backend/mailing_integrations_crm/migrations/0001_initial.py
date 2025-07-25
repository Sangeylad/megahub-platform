# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mailing_integrations_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CRMSync',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sync_direction', models.CharField(choices=[('bidirectional', 'Bidirectional'), ('crm_to_mailing', 'CRM to Mailing'), ('mailing_to_crm', 'Mailing to CRM')], default='bidirectional', max_length=30)),
                ('field_mapping', models.JSONField(default=dict)),
                ('sync_rules', models.JSONField(default=dict)),
                ('auto_sync_enabled', models.BooleanField(default=True)),
                ('sync_interval_hours', models.IntegerField(default=24)),
                ('last_successful_sync', models.DateTimeField(blank=True, null=True)),
                ('total_contacts_synced', models.IntegerField(default=0)),
                ('failed_sync_count', models.IntegerField(default=0)),
                ('integration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mailing_integrations_core.integration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SyncHistory',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sync_status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], max_length=20)),
                ('contacts_processed', models.IntegerField(default=0)),
                ('contacts_created', models.IntegerField(default=0)),
                ('contacts_updated', models.IntegerField(default=0)),
                ('contacts_failed', models.IntegerField(default=0)),
                ('sync_duration_seconds', models.IntegerField(default=0)),
                ('error_details', models.JSONField(default=dict)),
                ('started_at', models.DateTimeField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('crm_sync', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sync_history', to='mailing_integrations_crm.crmsync')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
