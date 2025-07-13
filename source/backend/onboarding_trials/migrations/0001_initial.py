# backend/onboarding_trials/migrations/0001_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_core', '0003_company_trial_expires_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrialEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.CharField(choices=[('trial_start', 'Trial démarré'), ('trial_warning_7', 'Avertissement 7 jours'), ('trial_warning_3', 'Avertissement 3 jours'), ('trial_warning_1', 'Avertissement 1 jour'), ('trial_expired', 'Trial expiré'), ('trial_extended', 'Trial étendu'), ('auto_upgrade', 'Upgrade automatique'), ('manual_upgrade', 'Upgrade manuel'), ('trial_converted', 'Trial converti')], help_text="Type d'événement trial", max_length=30)),
                ('event_data', models.JSONField(blank=True, default=dict, help_text="Données JSON de l'événement")),
                ('processed', models.BooleanField(default=False, help_text='Événement traité')),
                ('company', models.ForeignKey(help_text='Company concernée', on_delete=django.db.models.deletion.CASCADE, related_name='trial_events', to='company_core.company')),
                ('triggered_by', models.ForeignKey(blank=True, help_text="User qui a déclenché l'événement", null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'trial_event',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['company', 'event_type'], name='trial_event_company_aaf124_idx'), models.Index(fields=['event_type', 'processed'], name='trial_event_event_t_062813_idx'), models.Index(fields=['created_at'], name='trial_event_created_51b6ab_idx')],
            },
        ),
    ]
