# backend/blog_content/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('excerpt', models.TextField(blank=True, help_text='Résumé article', max_length=300)),
                ('featured_image_url', models.URLField(blank=True)),
                ('featured_image_alt', models.CharField(blank=True, max_length=200)),
                ('featured_image_caption', models.CharField(blank=True, max_length=300)),
                ('focus_keyword', models.CharField(blank=True, max_length=100)),
                ('word_count', models.PositiveIntegerField(default=0)),
                ('reading_time_minutes', models.PositiveIntegerField(default=5)),
            ],
            options={
                'verbose_name': 'Article Blog',
                'verbose_name_plural': 'Articles Blog',
                'db_table': 'blog_content_blogarticle',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BlogAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('display_name', models.CharField(help_text='Nom affiché publiquement', max_length=100)),
                ('bio', models.TextField(blank=True, help_text='Biographie courte', max_length=500)),
                ('avatar_url', models.URLField(blank=True)),
                ('website_url', models.URLField(blank=True)),
                ('twitter_handle', models.CharField(blank=True, max_length=50)),
                ('linkedin_url', models.URLField(blank=True)),
                ('expertise_topics', models.JSONField(blank=True, default=list, help_text="Sujets d'expertise ['SEO', 'Content Marketing']")),
                ('articles_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Auteur Blog',
                'verbose_name_plural': 'Auteurs Blog',
                'db_table': 'blog_content_blogauthor',
            },
        ),
        migrations.CreateModel(
            name='BlogTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6366f1', help_text='Couleur hexadécimale', max_length=7)),
                ('meta_title', models.CharField(blank=True, max_length=60)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
                ('usage_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Tag Blog',
                'verbose_name_plural': 'Tags Blog',
                'db_table': 'blog_content_blogtag',
                'ordering': ['name'],
            },
        ),
    ]
