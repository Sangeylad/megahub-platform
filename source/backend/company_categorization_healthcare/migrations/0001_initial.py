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
            name='HealthcareCompanyProfile',
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
                ('healthcare_type', models.CharField(choices=[('clinic', 'Clinique & Cabinet Médical'), ('hospital', 'Hôpital & Centre Hospitalier'), ('pharmacy', 'Pharmacie & Parapharmacie'), ('laboratory', "Laboratoire d'Analyses"), ('medtech', 'MedTech & Dispositifs Médicaux'), ('healthtech', 'HealthTech & E-santé'), ('insurance', 'Assurance Santé'), ('wellness', 'Bien-être & Prévention'), ('research', 'Recherche Médicale')], help_text="Type d'activité santé", max_length=20)),
                ('primary_specialty', models.CharField(choices=[('general', 'Médecine Générale'), ('cardiology', 'Cardiologie'), ('dermatology', 'Dermatologie'), ('pediatrics', 'Pédiatrie'), ('gynecology', 'Gynécologie'), ('orthopedics', 'Orthopédie'), ('psychiatry', 'Psychiatrie'), ('oncology', 'Oncologie'), ('ophthalmology', 'Ophtalmologie'), ('dentistry', 'Dentaire'), ('multi_specialty', 'Multi-spécialités')], default='general', help_text='Spécialité médicale principale', max_length=20)),
                ('health_license_number', models.CharField(blank=True, help_text="Numéro d'autorisation sanitaire", max_length=50)),
                ('accreditation_bodies', models.TextField(blank=True, help_text="Organismes d'accréditation (HAS, etc.)")),
                ('bed_capacity', models.IntegerField(blank=True, help_text="Capacité d'accueil (lits/places)", null=True)),
                ('staff_count', models.IntegerField(blank=True, help_text='Nombre de personnel médical', null=True)),
                ('consultation_rooms', models.IntegerField(blank=True, help_text='Nombre de salles de consultation', null=True)),
                ('emergency_services', models.BooleanField(default=False, help_text="Services d'urgence disponibles")),
                ('telemedicine_services', models.BooleanField(default=False, help_text='Services de télémédecine')),
                ('home_care_services', models.BooleanField(default=False, help_text='Services de soins à domicile')),
                ('has_imaging_equipment', models.BooleanField(default=False, help_text="Équipements d'imagerie (IRM, Scanner)")),
                ('has_surgery_facilities', models.BooleanField(default=False, help_text='Bloc opératoire disponible')),
                ('uses_ehr_system', models.BooleanField(default=False, help_text='Utilise un système de dossier médical électronique')),
                ('ehr_provider', models.CharField(blank=True, help_text='Fournisseur du système de DME', max_length=50)),
                ('has_patient_portal', models.BooleanField(default=False, help_text="Dispose d'un portail patient")),
                ('patients_per_month', models.IntegerField(blank=True, help_text='Nombre de patients par mois', null=True)),
                ('average_consultation_duration', models.IntegerField(blank=True, help_text='Durée moyenne consultation (minutes)', null=True)),
                ('company', models.OneToOneField(help_text='Entreprise associée à ce profil', on_delete=django.db.models.deletion.CASCADE, to='company_core.company')),
                ('validated_by', models.ForeignKey(blank=True, help_text='Expert qui a validé le profil', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil Santé',
                'verbose_name_plural': 'Profils Santé',
                'db_table': 'healthcare_company_profile',
                'indexes': [models.Index(fields=['healthcare_type'], name='healthcare__healthc_82838c_idx'), models.Index(fields=['primary_specialty'], name='healthcare__primary_d02d87_idx'), models.Index(fields=['telemedicine_services'], name='healthcare__telemed_44b266_idx')],
            },
        ),
    ]
