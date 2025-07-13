# backend/seo_websites_ai_templates_content/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_categories', '0001_initial'),
        ('ai_templates_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SEOWebsiteTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page_type', models.CharField(choices=[('landing', 'Landing Page'), ('vitrine', 'Page Vitrine'), ('service', 'Page Service'), ('produit', 'Page Produit'), ('blog', 'Article Blog'), ('category', 'Page Catégorie')], max_length=50)),
                ('search_intent', models.CharField(choices=[('TOFU', 'Top of Funnel'), ('MOFU', 'Middle of Funnel'), ('BOFU', 'Bottom of Funnel'), ('BRAND', 'Brand')], default='TOFU', max_length=20)),
                ('target_word_count', models.PositiveIntegerField(default=800, help_text='Nombre de mots cible')),
                ('keyword_density_target', models.FloatField(default=1.5, help_text='Densité mots-clés cible (%)')),
                ('base_template', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seo_config', to='ai_templates_core.basetemplate')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_templates_categories.templatecategory')),
            ],
            options={
                'db_table': 'seo_website_template',
            },
        ),
        migrations.CreateModel(
            name='SEOTemplateConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('h1_structure', models.CharField(default='{{target_keyword}} - {{brand_name}}', max_length=200)),
                ('h2_pattern', models.TextField(default='## {{secondary_keyword}}\n\n{{content_section}}')),
                ('meta_title_template', models.CharField(default='{{target_keyword}} | {{brand_name}}', max_length=200)),
                ('meta_description_template', models.TextField(default='{{description_intro}} {{target_keyword}} {{brand_name}}. {{cta_phrase}}')),
                ('internal_linking_rules', models.JSONField(default=dict, help_text='Règles de maillage interne')),
                ('schema_markup_type', models.CharField(blank=True, help_text='Type de schema.org', max_length=50)),
                ('seo_template', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='advanced_config', to='seo_websites_ai_templates_content.seowebsitetemplate')),
            ],
            options={
                'db_table': 'seo_template_config',
            },
        ),
        migrations.CreateModel(
            name='PageTypeTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('page_type', models.CharField(max_length=50)),
                ('template_structure', models.TextField(help_text='Structure template avec sections')),
                ('default_sections', models.JSONField(default=list, help_text='Sections par défaut')),
                ('required_variables', models.JSONField(default=list, help_text='Variables obligatoires')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'page_type_template',
                'unique_together': {('name', 'page_type')},
            },
        ),
        migrations.CreateModel(
            name='KeywordIntegrationRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('keyword_type', models.CharField(choices=[('primary', 'Principal'), ('secondary', 'Secondaire'), ('anchor', 'Ancre'), ('semantic', 'Sémantique')], max_length=20)),
                ('placement_rules', models.JSONField(default=dict, help_text='Règles de placement (H1, H2, paragraphes)')),
                ('density_min', models.FloatField(default=0.5, help_text='Densité minimum (%)')),
                ('density_max', models.FloatField(default=3.0, help_text='Densité maximum (%)')),
                ('natural_variations', models.BooleanField(default=True, help_text='Utiliser variations naturelles')),
                ('seo_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyword_rules', to='seo_websites_ai_templates_content.seowebsitetemplate')),
            ],
            options={
                'db_table': 'keyword_integration_rule',
            },
        ),
        migrations.AddIndex(
            model_name='seowebsitetemplate',
            index=models.Index(fields=['page_type', 'search_intent'], name='seo_website_page_ty_e1d54a_idx'),
        ),
        migrations.AddIndex(
            model_name='seowebsitetemplate',
            index=models.Index(fields=['category'], name='seo_website_categor_dd9953_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='keywordintegrationrule',
            unique_together={('seo_template', 'keyword_type')},
        ),
    ]
