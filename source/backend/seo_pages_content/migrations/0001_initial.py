# backend/seo_pages_content/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_websites_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('url_path', models.CharField(blank=True, max_length=500)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('search_intent', models.CharField(blank=True, choices=[('TOFU', 'Top of Funnel'), ('MOFU', 'Middle of Funnel'), ('BOFU', 'Bottom of Funnel')], max_length=10, null=True)),
                ('page_type', models.CharField(choices=[('vitrine', 'Vitrine'), ('blog', 'Blog'), ('blog_category', 'Catégorie Blog'), ('produit', 'Produit/Service'), ('landing', 'Landing Page'), ('categorie', 'Page Catégorie'), ('legal', 'Page Légale'), ('outils', 'Outils'), ('autre', 'Autre')], default='vitrine', max_length=20)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='seo_websites_core.website')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'db_table': 'seo_pages_content_page',
                'ordering': ['website', 'url_path', '-created_at'],
                'indexes': [models.Index(fields=['website', 'page_type'], name='seo_pages_c_website_363f24_idx'), models.Index(fields=['url_path'], name='seo_pages_c_url_pat_1dff1a_idx')],
                'unique_together': {('website', 'url_path')},
            },
        ),
    ]
