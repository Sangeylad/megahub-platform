# backend/seo_keywords_content_types/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_keywords_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'seo_keywords_content_types_contenttype',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='KeywordContentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyword_associations', to='seo_keywords_content_types.contenttype')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_associations', to='seo_keywords_base.keyword')),
            ],
            options={
                'db_table': 'seo_keywords_content_types_keywordcontenttype',
                'ordering': ['keyword', 'priority'],
                'unique_together': {('keyword', 'content_type')},
            },
        ),
    ]
