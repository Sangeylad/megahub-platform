# Generated by Django 4.2.23 on 2025-07-26 20:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm_entities_core', '0002_initial'),
        ('brands_core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSubscriber',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$')])),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active'), ('unsubscribed', 'Unsubscribed'), ('bounced', 'Bounced'), ('pending', 'Pending'), ('complaint', 'Complaint')], default='active', max_length=20)),
                ('source', models.CharField(choices=[('manual', 'Manual'), ('import', 'Import'), ('api', 'API'), ('form', 'Form'), ('integration', 'Integration'), ('crm_sync', 'CRM Sync'), ('landing_page', 'Landing Page'), ('popup', 'Popup'), ('webinar', 'Webinar'), ('event', 'Event')], default='manual', max_length=50)),
                ('language', models.CharField(choices=[('fr', 'Français'), ('en', 'English'), ('es', 'Español'), ('de', 'Deutsch'), ('it', 'Italiano'), ('pt', 'Português')], default='fr', max_length=10)),
                ('timezone', models.CharField(choices=[('Europe/Paris', 'Europe/Paris'), ('Europe/London', 'Europe/London'), ('America/New_York', 'America/New_York'), ('America/Los_Angeles', 'America/Los_Angeles'), ('Asia/Tokyo', 'Asia/Tokyo'), ('Australia/Sydney', 'Australia/Sydney')], default='Europe/Paris', max_length=50)),
                ('crm_contact', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm_entities_core.contact')),
                ('source_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
            ],
            options={
                'indexes': [models.Index(fields=['status', 'source_brand'], name='mailing_con_status_885260_idx'), models.Index(fields=['email'], name='mailing_con_email_8dad30_idx'), models.Index(fields=['created_at'], name='mailing_con_created_11098a_idx')],
                'unique_together': {('email', 'source_brand')},
            },
        ),
    ]
