# backend/brands_design_colors/migrations/0001_initial.py

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
            name='WebsiteColorConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('primary_override', models.CharField(blank=True, help_text='Override couleur primaire pour ce site', max_length=7)),
                ('secondary_override', models.CharField(blank=True, help_text='Override couleur secondaire pour ce site', max_length=7)),
                ('accent_override', models.CharField(blank=True, help_text='Override couleur accent pour ce site', max_length=7)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='color_config', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Configuration Couleurs Website',
                'verbose_name_plural': 'Configurations Couleurs Websites',
                'db_table': 'brands_design_colors_website',
            },
        ),
        migrations.CreateModel(
            name='BrandColorPalette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('primary_color', models.CharField(help_text='Couleur primaire (ex: #FF6B35)', max_length=7)),
                ('secondary_color', models.CharField(help_text='Couleur secondaire (ex: #F7931E)', max_length=7)),
                ('accent_color', models.CharField(help_text="Couleur d'accent (ex: #FFD23F)", max_length=7)),
                ('neutral_dark', models.CharField(default='#1A1A1A', help_text='Couleur neutre sombre', max_length=7)),
                ('neutral_light', models.CharField(default='#F8F9FA', help_text='Couleur neutre claire', max_length=7)),
                ('success_color', models.CharField(default='#10B981', max_length=7)),
                ('warning_color', models.CharField(default='#F59E0B', max_length=7)),
                ('error_color', models.CharField(default='#EF4444', max_length=7)),
                ('brand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='color_palette', to='brands_core.brand')),
            ],
            options={
                'verbose_name': 'Palette de Couleurs',
                'verbose_name_plural': 'Palettes de Couleurs',
                'db_table': 'brands_design_colors_palette',
            },
        ),
    ]
