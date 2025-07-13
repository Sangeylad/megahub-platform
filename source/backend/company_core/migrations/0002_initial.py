# backend/company_core/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='admin',
            field=models.OneToOneField(help_text="Administrateur principal de l'entreprise", on_delete=django.db.models.deletion.CASCADE, related_name='admin_company', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['is_active'], name='company_is_acti_997df1_idx'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['stripe_customer_id'], name='company_stripe__97f456_idx'),
        ),
    ]
