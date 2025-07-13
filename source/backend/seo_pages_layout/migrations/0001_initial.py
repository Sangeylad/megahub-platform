# backend/seo_pages_layout/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PageLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('render_strategy', models.CharField(choices=[('sections', 'Page Builder Sections'), ('markdown', 'Markdown Content'), ('custom', 'Custom Template')], default='sections', max_length=20)),
                ('layout_data', models.JSONField(default=dict, help_text='Configuration JSON pour le renderer')),
            ],
            options={
                'verbose_name': 'Configuration Layout',
                'verbose_name_plural': 'Configurations Layout',
                'db_table': 'seo_pages_layout_layout',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='PageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section_type', models.CharField(choices=[('layout_columns', 'Layout en Colonnes'), ('layout_grid', 'Layout en Grille'), ('layout_stack', 'Layout Vertical'), ('hero_banner', 'Hero Banner'), ('cta_banner', 'CTA Banner'), ('features_grid', 'Features Grid'), ('rich_text', 'Rich Text Block')], max_length=50)),
                ('data', models.JSONField(blank=True, default=dict, help_text='Props JSON pour React')),
                ('layout_config', models.JSONField(blank=True, default=dict, help_text="Config CSS Grid : {columns: [8, 4], gap: '2rem'}")),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.CharField(default='1.0', max_length=10)),
            ],
            options={
                'verbose_name': 'Section de Page',
                'verbose_name_plural': 'Sections de Page',
                'db_table': 'seo_pages_layout_section',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
