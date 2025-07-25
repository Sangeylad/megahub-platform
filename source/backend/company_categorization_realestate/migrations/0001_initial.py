# Generated by Django 4.2.23 on 2025-07-21 17:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company_core', '0003_company_trial_expires_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RealEstateCompanyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('additional_info', models.JSONField(blank=True, default=dict, help_text='Informations additionnelles spécifiques au secteur')),
                ('industry_score', models.IntegerField(blank=True, help_text="Score d'adéquation avec le secteur (0-100)", null=True)),
                ('is_validated', models.BooleanField(default=False, help_text='Profil validé par un expert secteur')),
                ('validated_at', models.DateTimeField(blank=True, help_text='Date de validation', null=True)),
                ('business_type', models.CharField(choices=[('agency', 'Agence Immobilière'), ('developer', 'Promoteur Immobilier'), ('property_mgmt', 'Gestion Locative'), ('investment', 'Investissement Immobilier'), ('construction', 'Construction & BTP'), ('proptech', 'PropTech & Innovation'), ('consulting', 'Conseil Immobilier'), ('commercial', 'Immobilier Commercial'), ('luxury', 'Immobilier de Luxe')], help_text="Type d'activité immobilière", max_length=20)),
                ('activity_focus', models.CharField(choices=[('residential', 'Résidentiel'), ('commercial', 'Commercial'), ('industrial', 'Industriel'), ('mixed', 'Mixte'), ('luxury', 'Luxe'), ('new_build', 'Neuf'), ('renovation', 'Rénovation')], help_text="Focus d'activité principal", max_length=15)),
                ('primary_market', models.CharField(help_text='Marché géographique principal', max_length=100)),
                ('coverage_area', models.TextField(blank=True, help_text='Zone de couverture géographique')),
                ('properties_under_management', models.IntegerField(blank=True, help_text='Nombre de biens en gestion', null=True)),
                ('average_property_value', models.DecimalField(blank=True, decimal_places=2, help_text='Valeur moyenne des biens (€)', max_digits=12, null=True)),
                ('transactions_per_year', models.IntegerField(blank=True, help_text='Nombre de transactions annuelles', null=True)),
                ('luxury_specialist', models.BooleanField(default=False, help_text='Spécialisé dans le luxe')),
                ('first_time_buyers_focus', models.BooleanField(default=False, help_text='Focus primo-accédants')),
                ('investment_focus', models.BooleanField(default=False, help_text='Focus investissement locatif')),
                ('certifications', models.TextField(blank=True, help_text='Certifications professionnelles (FNAIM, etc.)')),
                ('insurance_coverage', models.CharField(blank=True, help_text='Assurance responsabilité civile professionnelle', max_length=100)),
                ('uses_virtual_tours', models.BooleanField(default=False, help_text='Utilise la visite virtuelle')),
                ('has_mobile_app', models.BooleanField(default=False, help_text="Dispose d'une app mobile")),
                ('crm_system', models.CharField(blank=True, help_text='Système CRM utilisé', max_length=50)),
                ('company', models.OneToOneField(help_text='Entreprise associée à ce profil', on_delete=django.db.models.deletion.CASCADE, to='company_core.company')),
                ('validated_by', models.ForeignKey(blank=True, help_text='Expert qui a validé le profil', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil Immobilier',
                'verbose_name_plural': 'Profils Immobiliers',
                'db_table': 'realestate_company_profile',
                'indexes': [models.Index(fields=['business_type'], name='realestate__busines_0fd2f9_idx'), models.Index(fields=['activity_focus'], name='realestate__activit_83adc3_idx'), models.Index(fields=['luxury_specialist'], name='realestate__luxury__a8ade1_idx')],
            },
        ),
    ]
