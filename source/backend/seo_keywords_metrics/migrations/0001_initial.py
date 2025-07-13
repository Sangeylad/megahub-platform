# backend/seo_keywords_metrics/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_keywords_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('da_min', models.IntegerField(blank=True, null=True)),
                ('da_max', models.IntegerField(blank=True, null=True)),
                ('da_median', models.IntegerField(blank=True, null=True)),
                ('da_q1', models.IntegerField(blank=True, null=True)),
                ('da_q3', models.IntegerField(blank=True, null=True)),
                ('bl_min', models.IntegerField(blank=True, null=True)),
                ('bl_max', models.IntegerField(blank=True, null=True)),
                ('bl_median', models.IntegerField(blank=True, null=True)),
                ('bl_q1', models.IntegerField(blank=True, null=True)),
                ('bl_q3', models.IntegerField(blank=True, null=True)),
                ('kdifficulty', models.CharField(blank=True, max_length=200, null=True)),
                ('keyword', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='seo_keywords_base.keyword')),
            ],
            options={
                'db_table': 'seo_keywords_metrics_keywordmetrics',
                'ordering': ['keyword__keyword'],
            },
        ),
    ]
