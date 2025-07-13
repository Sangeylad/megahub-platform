# backend/seo_keywords_base/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('keyword', models.CharField(max_length=1000, unique=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('search_intent', models.CharField(blank=True, choices=[('TOFU', 'Top of Funnel'), ('MOFU', 'Middle of Funnel'), ('BOFU', 'Bottom of Funnel')], max_length=10, null=True)),
                ('cpc', models.CharField(blank=True, max_length=50, null=True)),
                ('youtube_videos', models.CharField(blank=True, max_length=500, null=True)),
                ('local_pack', models.BooleanField(default=False)),
                ('search_results', models.JSONField(blank=True, default=dict)),
                ('content_types', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'seo_keywords_base_keyword',
                'ordering': ['-volume', 'keyword'],
                'indexes': [models.Index(fields=['keyword'], name='seo_keyword_keyword_293ad7_idx'), models.Index(fields=['volume'], name='seo_keyword_volume_80f3e1_idx'), models.Index(fields=['search_intent'], name='seo_keyword_search__cdf371_idx')],
            },
        ),
    ]
