# backend/seo_keywords_ppa/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_keywords_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PPA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.TextField(unique=True)),
            ],
            options={
                'db_table': 'seo_keywords_ppa_ppa',
                'ordering': ['question'],
            },
        ),
        migrations.CreateModel(
            name='KeywordPPA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('position', models.IntegerField()),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ppa_associations', to='seo_keywords_base.keyword')),
                ('ppa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyword_associations', to='seo_keywords_ppa.ppa')),
            ],
            options={
                'db_table': 'seo_keywords_ppa_keywordppa',
                'ordering': ['keyword', 'position'],
                'unique_together': {('keyword', 'ppa', 'position')},
            },
        ),
    ]
