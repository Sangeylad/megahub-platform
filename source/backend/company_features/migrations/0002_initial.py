# backend/company_features/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_features', '0001_initial'),
        ('company_core', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureusagelog',
            name='user',
            field=models.ForeignKey(blank=True, help_text="Utilisateur qui a effectué l'action", null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='feature',
            index=models.Index(fields=['is_active'], name='feature_is_acti_05642f_idx'),
        ),
        migrations.AddIndex(
            model_name='feature',
            index=models.Index(fields=['is_premium'], name='feature_is_prem_285b12_idx'),
        ),
        migrations.AddIndex(
            model_name='feature',
            index=models.Index(fields=['feature_type'], name='feature_feature_8618b6_idx'),
        ),
        migrations.AddField(
            model_name='companyfeature',
            name='company',
            field=models.ForeignKey(help_text='Entreprise abonnée à la feature', on_delete=django.db.models.deletion.CASCADE, related_name='company_features', to='company_core.company'),
        ),
        migrations.AddField(
            model_name='companyfeature',
            name='feature',
            field=models.ForeignKey(help_text='Feature souscrite', on_delete=django.db.models.deletion.CASCADE, related_name='subscribed_companies', to='company_features.feature'),
        ),
        migrations.AddIndex(
            model_name='featureusagelog',
            index=models.Index(fields=['company_feature', 'created_at'], name='feature_usa_company_3f5420_idx'),
        ),
        migrations.AddIndex(
            model_name='featureusagelog',
            index=models.Index(fields=['user', 'created_at'], name='feature_usa_user_id_af68c9_idx'),
        ),
        migrations.AddIndex(
            model_name='featureusagelog',
            index=models.Index(fields=['action'], name='feature_usa_action_c7fb58_idx'),
        ),
        migrations.AddIndex(
            model_name='companyfeature',
            index=models.Index(fields=['is_enabled'], name='company_fea_is_enab_594f54_idx'),
        ),
        migrations.AddIndex(
            model_name='companyfeature',
            index=models.Index(fields=['expires_at'], name='company_fea_expires_318999_idx'),
        ),
        migrations.AddIndex(
            model_name='companyfeature',
            index=models.Index(fields=['company', 'is_enabled'], name='company_fea_company_d02c81_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='companyfeature',
            unique_together={('company', 'feature')},
        ),
    ]
