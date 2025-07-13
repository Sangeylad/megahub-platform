# backend/brands_core/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='brand_admin',
            field=models.ForeignKey(blank=True, help_text='Administrateur de la marque (unique par sécurité)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='administered_brands', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='brand',
            name='company',
            field=models.ForeignKey(help_text='Entreprise propriétaire de la marque', on_delete=django.db.models.deletion.CASCADE, related_name='brands', to='company_core.company'),
        ),
        migrations.AddIndex(
            model_name='brand',
            index=models.Index(fields=['company', 'is_active'], name='brand_company_911aa5_idx'),
        ),
        migrations.AddIndex(
            model_name='brand',
            index=models.Index(fields=['brand_admin'], name='brand_brand_a_6f5bde_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='brand',
            unique_together={('company', 'name')},
        ),
    ]
