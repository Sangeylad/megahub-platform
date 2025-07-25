# Generated by Django 4.2.23 on 2025-07-26 20:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('subject_line', models.CharField(max_length=300)),
                ('preview_text', models.CharField(blank=True, max_length=150)),
                ('campaign_type', models.CharField(choices=[('newsletter', 'Newsletter'), ('promotional', 'Promotional'), ('announcement', 'Announcement'), ('product_update', 'Product Update'), ('event', 'Event'), ('welcome', 'Welcome'), ('nurturing', 'Nurturing'), ('reengagement', 'Re-engagement'), ('transactional', 'Transactional'), ('automation', 'Automation')], default='newsletter', max_length=30)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('sending', 'Sending'), ('sent', 'Sent'), ('paused', 'Paused'), ('cancelled', 'Cancelled'), ('failed', 'Failed')], default='draft', max_length=20)),
                ('html_content', models.TextField(blank=True)),
                ('text_content', models.TextField(blank=True)),
                ('from_name', models.CharField(max_length=100)),
                ('from_email', models.EmailField(max_length=254)),
                ('reply_to_email', models.EmailField(blank=True, max_length=254)),
                ('send_time_optimization', models.CharField(choices=[('immediate', 'Send Immediately'), ('time_zone', 'Optimize by Time Zone'), ('engagement', 'Optimize by Engagement'), ('send_time', 'Send Time Optimization')], default='immediate', max_length=20)),
                ('scheduled_send_time', models.DateTimeField(blank=True, null=True)),
                ('ab_test_enabled', models.BooleanField(default=False)),
                ('ab_test_config', models.JSONField(default=dict)),
                ('tags', models.JSONField(default=list)),
                ('total_recipients', models.IntegerField(default=0)),
                ('emails_sent', models.IntegerField(default=0)),
                ('emails_delivered', models.IntegerField(default=0)),
                ('emails_opened', models.IntegerField(default=0)),
                ('emails_clicked', models.IntegerField(default=0)),
                ('emails_bounced', models.IntegerField(default=0)),
                ('emails_unsubscribed', models.IntegerField(default=0)),
                ('open_rate', models.DecimalField(decimal_places=4, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('click_rate', models.DecimalField(decimal_places=4, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignList',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('recipients_count', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailing_campaigns_core.campaign')),
            ],
        ),
    ]
