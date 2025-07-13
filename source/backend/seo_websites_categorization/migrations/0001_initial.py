# backend/seo_websites_categorization/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteCategorization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_primary', models.BooleanField(default=False, help_text='Catégorie principale du website')),
                ('confidence_score', models.FloatField(blank=True, help_text='Score de confiance de la catégorisation (0.0-1.0)', null=True)),
                ('source', models.CharField(choices=[('manual', 'Manuelle'), ('automatic', 'Automatique'), ('ai_suggested', 'Suggérée par IA'), ('imported', 'Importée')], default='manual', max_length=20)),
                ('notes', models.TextField(blank=True, help_text='Notes sur cette catégorisation')),
            ],
            options={
                'verbose_name': 'Catégorisation de Website',
                'verbose_name_plural': 'Catégorisations de Websites',
                'db_table': 'seo_websites_categorization_association',
                'ordering': ['-is_primary', 'category__name'],
            },
        ),
        migrations.CreateModel(
            name='WebsiteCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6366f1', help_text="Couleur hexadécimale pour l'interface", max_length=7)),
                ('typical_da_range_min', models.IntegerField(blank=True, help_text='DA minimum typique pour cette catégorie', null=True)),
                ('typical_da_range_max', models.IntegerField(blank=True, help_text='DA maximum typique pour cette catégorie', null=True)),
                ('typical_pages_count', models.IntegerField(blank=True, help_text='Nombre de pages typique', null=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='seo_websites_categorization.websitecategory')),
            ],
            options={
                'verbose_name': 'Catégorie de Website',
                'verbose_name_plural': 'Catégories de Websites',
                'db_table': 'seo_websites_categorization_category',
                'ordering': ['display_order', 'name'],
            },
        ),
    ]
