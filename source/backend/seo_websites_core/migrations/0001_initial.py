# backend/seo_websites_core/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('domain_authority', models.IntegerField(blank=True, help_text='Autorité de domaine de notre site', null=True)),
                ('max_competitor_backlinks', models.IntegerField(blank=True, help_text='Nombre maximal de backlinks de la concurrence', null=True)),
                ('max_competitor_kd', models.FloatField(blank=True, help_text='Difficulté keyword maximale des concurrents', null=True)),
                ('brand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seo_website', to='brands_core.brand')),
            ],
            options={
                'verbose_name': 'Site Web',
                'verbose_name_plural': 'Sites Web',
                'db_table': 'seo_websites_core_website',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['brand'], name='seo_website_brand_i_21053e_idx')],
            },
        ),
    ]
