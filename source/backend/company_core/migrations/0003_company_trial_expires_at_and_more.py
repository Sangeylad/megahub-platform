# backend/company_core/migrations/0003_company_trial_expires_at_and_more.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_core', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='trial_expires_at',
            field=models.DateTimeField(blank=True, help_text="Date d'expiration du trial (2 semaines)", null=True),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['trial_expires_at'], name='company_trial_e_55f227_idx'),
        ),
    ]
