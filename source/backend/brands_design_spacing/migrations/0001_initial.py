# backend/brands_design_spacing/migrations/0001_initial.py

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
            name='WebsiteLayoutConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('max_width_override', models.CharField(blank=True, help_text='Override largeur max pour ce site', max_length=20)),
                ('grid_columns_override', models.IntegerField(blank=True, help_text='Override nombre colonnes pour ce site', null=True)),
                ('sidebar_width', models.IntegerField(default=280, help_text='Largeur sidebar en px')),
                ('header_height', models.IntegerField(default=80, help_text='Hauteur header en px')),
                ('footer_height', models.IntegerField(default=120, help_text='Hauteur footer en px')),
                ('nav_collapse_breakpoint', models.CharField(choices=[('sm', 'Small (640px)'), ('md', 'Medium (768px)'), ('lg', 'Large (1024px)')], default='md', help_text='Breakpoint collapse navigation', max_length=10)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='layout_config', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Configuration Layout Website',
                'verbose_name_plural': 'Configurations Layout Websites',
                'db_table': 'brands_design_spacing_website',
            },
        ),
        migrations.CreateModel(
            name='BrandSpacingSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('base_unit', models.IntegerField(default=8, help_text='Unité de base en px (4, 8, 16)')),
                ('spacing_scale', models.FloatField(default=1.0, help_text="Multiplicateur d'espacement (0.8-1.2)")),
                ('max_width', models.CharField(default='1200px', help_text='Largeur max container', max_length=20)),
                ('container_padding', models.IntegerField(default=24, help_text='Padding container en px')),
                ('grid_columns', models.IntegerField(default=12, help_text='Nombre de colonnes grid')),
                ('grid_gap', models.IntegerField(default=24, help_text='Espacement entre colonnes en px')),
                ('breakpoint_sm', models.IntegerField(default=640)),
                ('breakpoint_md', models.IntegerField(default=768)),
                ('breakpoint_lg', models.IntegerField(default=1024)),
                ('breakpoint_xl', models.IntegerField(default=1280)),
                ('brand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spacing_system', to='brands_core.brand')),
            ],
            options={
                'verbose_name': 'Système Espacement',
                'verbose_name_plural': 'Systèmes Espacement',
                'db_table': 'brands_design_spacing_brand',
            },
        ),
    ]
