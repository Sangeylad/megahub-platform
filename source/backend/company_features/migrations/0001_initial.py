# backend/company_features/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.BooleanField(default=True, help_text='Feature activée pour cette entreprise')),
                ('usage_limit', models.IntegerField(blank=True, help_text="Limite d'utilisation pour cette feature (null = illimité)", null=True)),
                ('current_usage', models.IntegerField(default=0, help_text='Utilisation actuelle')),
                ('subscribed_at', models.DateTimeField(auto_now_add=True, help_text='Date de souscription à la feature')),
                ('expires_at', models.DateTimeField(blank=True, help_text="Date d'expiration (null = pas d'expiration)", null=True)),
            ],
            options={
                'db_table': 'company_feature',
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Nom technique de la feature', max_length=100, unique=True)),
                ('display_name', models.CharField(help_text="Nom d'affichage de la feature", max_length=150)),
                ('description', models.TextField(help_text='Description détaillée de la feature')),
                ('feature_type', models.CharField(choices=[('websites', 'Sites Web'), ('templates', 'Templates IA'), ('tasks', 'Gestion de tâches'), ('analytics', 'Analytics'), ('crm', 'CRM'), ('integrations', 'Intégrations')], default='websites', help_text='Type de feature', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Feature disponible sur la plateforme')),
                ('is_premium', models.BooleanField(default=False, help_text='Feature premium (payante)')),
                ('sort_order', models.IntegerField(default=0, help_text="Ordre d'affichage dans l'interface")),
            ],
            options={
                'db_table': 'feature',
                'ordering': ['sort_order', 'display_name'],
            },
        ),
        migrations.CreateModel(
            name='FeatureUsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(help_text="Action effectuée (ex: 'website_created', 'ai_request')", max_length=100)),
                ('quantity', models.IntegerField(default=1, help_text='Quantité utilisée')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Données supplémentaires en JSON')),
                ('brand', models.ForeignKey(blank=True, help_text="Brand concernée par l'action", null=True, on_delete=django.db.models.deletion.SET_NULL, to='brands_core.brand')),
                ('company_feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='company_features.companyfeature')),
            ],
            options={
                'verbose_name': 'Feature Usage Log',
                'verbose_name_plural': 'Feature Usage Logs',
                'db_table': 'feature_usage_log',
                'ordering': ['-created_at'],
            },
        ),
    ]
