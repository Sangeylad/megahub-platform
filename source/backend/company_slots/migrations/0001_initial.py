# backend/company_slots/migrations/0001_initial.py

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanySlots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('brands_slots', models.IntegerField(default=5, help_text='Nombre de brands maximum autorisées', validators=[django.core.validators.MinValueValidator(1)])),
                ('users_slots', models.IntegerField(default=10, help_text="Nombre d'utilisateurs maximum autorisés", validators=[django.core.validators.MinValueValidator(1)])),
                ('current_brands_count', models.IntegerField(default=0, help_text='Nombre de brands actuellement créées')),
                ('current_users_count', models.IntegerField(default=0, help_text="Nombre d'utilisateurs actuellement créés")),
                ('last_brands_count_update', models.DateTimeField(auto_now=True)),
                ('last_users_count_update', models.DateTimeField(auto_now=True)),
                ('company', models.OneToOneField(help_text='Entreprise propriétaire des slots', on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='company_core.company')),
            ],
            options={
                'verbose_name': 'Company Slots',
                'verbose_name_plural': 'Company Slots',
                'db_table': 'company_slots',
                'indexes': [models.Index(fields=['company'], name='company_slo_company_96800f_idx')],
            },
        ),
    ]
