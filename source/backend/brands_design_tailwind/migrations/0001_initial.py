# backend/brands_design_tailwind/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_websites_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteTailwindConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tailwind_config', models.JSONField(default=dict, help_text='Configuration theme.extend Tailwind')),
                ('css_variables', models.TextField(blank=True, help_text='Variables CSS générées')),
                ('last_generated_at', models.DateTimeField(blank=True, null=True)),
                ('config_hash', models.CharField(help_text='Hash pour invalidation cache', max_length=64)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tailwind_config', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Configuration Tailwind Website',
                'verbose_name_plural': 'Configurations Tailwind Websites',
                'db_table': 'brands_design_tailwind_website',
            },
        ),
        migrations.CreateModel(
            name='TailwindThemeExport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('export_type', models.CharField(choices=[('config', 'Config JS'), ('css', 'CSS Variables'), ('json', 'JSON Export')], max_length=20)),
                ('content', models.TextField(help_text='Contenu exporté')),
                ('file_hash', models.CharField(max_length=64)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tailwind_exports', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Export Tailwind',
                'verbose_name_plural': 'Exports Tailwind',
                'db_table': 'brands_design_tailwind_export',
                'unique_together': {('website', 'export_type')},
            },
        ),
    ]
