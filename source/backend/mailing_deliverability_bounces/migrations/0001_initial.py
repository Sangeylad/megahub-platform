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
            name='BounceHandling',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bounce_type', models.CharField(choices=[('hard', 'Hard'), ('soft', 'Soft'), ('block', 'Block'), ('invalid', 'Invalid'), ('unknown', 'Unknown')], max_length=30)),
                ('bounce_subtype', models.CharField(blank=True, choices=[('mailbox_full', 'Mailbox Full'), ('mailbox_not_found', 'Mailbox Not Found'), ('content_rejected', 'Content Rejected'), ('policy_violation', 'Policy Violation'), ('reputation_issue', 'Reputation Issue'), ('authentication_failed', 'Authentication Failed'), ('size_limit_exceeded', 'Size Limit Exceeded'), ('temporary_failure', 'Temporary Failure'), ('unknown', 'Unknown')], max_length=50)),
                ('smtp_code', models.CharField(blank=True, max_length=10)),
                ('smtp_message', models.TextField(blank=True)),
                ('bounce_category', models.CharField(blank=True, max_length=30)),
                ('action_taken', models.CharField(choices=[('none', 'None'), ('suppressed', 'Suppressed'), ('flagged', 'Flagged'), ('retry', 'Retry')], default='none', max_length=30)),
                ('retry_count', models.IntegerField(default=0)),
                ('will_retry', models.BooleanField(default=False)),
                ('next_retry', models.DateTimeField(blank=True, null=True)),
                ('email_event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mailing_analytics_core.emailevent')),
            ],
        ),
    ]
