# backend/brands_design_typography/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_websites_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteTypographyConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('font_primary_override', models.CharField(blank=True, help_text='Override font primaire pour ce site', max_length=100)),
                ('base_font_size_override', models.IntegerField(blank=True, help_text='Override taille base pour ce site', null=True)),
                ('scale_ratio_override', models.FloatField(blank=True, help_text='Override ratio échelle pour ce site', null=True)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='typography_config', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Configuration Typographie Website',
                'verbose_name_plural': 'Configurations Typographie Websites',
                'db_table': 'brands_design_typography_website',
            },
        ),
        migrations.CreateModel(
            name='BrandTypography',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('font_primary', models.CharField(help_text='Font principale (ex: Inter, Roboto)', max_length=100)),
                ('font_secondary', models.CharField(blank=True, help_text='Font secondaire (ex: Roboto Slab)', max_length=100)),
                ('font_mono', models.CharField(default='Fira Code', help_text='Font monospace pour code', max_length=100)),
                ('google_fonts_url', models.URLField(blank=True, help_text='URL Google Fonts à charger')),
                ('base_font_size', models.IntegerField(default=16, help_text='Taille de base en px')),
                ('scale_ratio', models.FloatField(default=1.25, help_text="Ratio d'échelle typographique (1.125, 1.25, 1.5)")),
                ('base_line_height', models.FloatField(default=1.6, help_text='Hauteur de ligne de base')),
                ('brand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='typography', to='brands_core.brand')),
            ],
            options={
                'verbose_name': 'Typographie Marque',
                'verbose_name_plural': 'Typographies Marques',
                'db_table': 'brands_design_typography_brand',
            },
        ),
    ]
