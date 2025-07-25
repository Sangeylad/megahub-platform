# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mailing_analytics_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailOpen',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_unique', models.BooleanField(default=True)),
                ('open_count', models.IntegerField(default=1)),
                ('email_client', models.CharField(blank=True, choices=[('gmail', 'Gmail'), ('outlook', 'Outlook'), ('apple_mail', 'Apple Mail'), ('yahoo', 'Yahoo Mail'), ('thunderbird', 'Thunderbird'), ('webmail', 'Webmail'), ('mobile_app', 'Mobile App'), ('other', 'Other')], max_length=100)),
                ('device_type', models.CharField(blank=True, choices=[('mobile', 'Mobile'), ('desktop', 'Desktop'), ('tablet', 'Tablet'), ('smart_tv', 'Smart TV'), ('wearable', 'Wearable'), ('other', 'Other')], max_length=30)),
                ('operating_system', models.CharField(blank=True, choices=[('windows', 'Windows'), ('macos', 'macOS'), ('ios', 'iOS'), ('android', 'Android'), ('linux', 'Linux'), ('other', 'Other')], max_length=50)),
                ('location_country', models.CharField(blank=True, max_length=100)),
                ('location_region', models.CharField(blank=True, max_length=100)),
                ('location_city', models.CharField(blank=True, max_length=100)),
                ('timezone', models.CharField(blank=True, max_length=50)),
                ('forwarded', models.BooleanField(default=False)),
                ('email_event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mailing_analytics_core.emailevent')),
            ],
        ),
    ]
