# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mailing_automations_actions', '0001_initial'),
        ('mailing_automations_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='automationaction',
            name='automation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='mailing_automations_core.automation'),
        ),
        migrations.AddField(
            model_name='automationaction',
            name='parent_action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mailing_automations_actions.automationaction'),
        ),
    ]
