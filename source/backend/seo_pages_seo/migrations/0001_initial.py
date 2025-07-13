# backend/seo_pages_seo/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageSEO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured_image', models.URLField(blank=True, help_text='Image principale pour réseaux sociaux', null=True)),
                ('sitemap_priority', models.DecimalField(decimal_places=1, default=0.5, help_text='Priorité relative (0.0 à 1.0)', max_digits=2)),
                ('sitemap_changefreq', models.CharField(choices=[('always', 'Always'), ('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly'), ('never', 'Never')], default='weekly', max_length=20)),
                ('exclude_from_sitemap', models.BooleanField(default=False, help_text='Exclure de sitemap.xml')),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seo_config', to='seo_pages_content.page')),
            ],
            options={
                'verbose_name': 'Configuration SEO',
                'verbose_name_plural': 'Configurations SEO',
                'db_table': 'seo_pages_seo_seo',
                'ordering': ['-updated_at'],
                'indexes': [models.Index(fields=['page', 'sitemap_priority'], name='seo_pages_s_page_id_c93377_idx')],
            },
        ),
        migrations.CreateModel(
            name='PagePerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_rendered_at', models.DateTimeField(blank=True, help_text='Dernière génération statique', null=True)),
                ('render_time_ms', models.PositiveIntegerField(blank=True, help_text='Temps de rendu en millisecondes', null=True)),
                ('cache_hits', models.PositiveIntegerField(default=0, help_text='Nombre de hits cache')),
                ('last_crawled_at', models.DateTimeField(blank=True, help_text='Dernière visite crawler Google', null=True)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='performance', to='seo_pages_content.page')),
            ],
            options={
                'verbose_name': 'Performance de Page',
                'verbose_name_plural': 'Performances de Page',
                'db_table': 'seo_pages_seo_performance',
                'ordering': ['-updated_at'],
                'indexes': [models.Index(fields=['page', 'last_rendered_at'], name='seo_pages_s_page_id_f2e88a_idx')],
            },
        ),
    ]
