# backend/blog_config/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blog_name', models.CharField(help_text='Nom affiché du blog', max_length=100)),
                ('blog_slug', models.SlugField(help_text='Slug URL du blog')),
                ('blog_description', models.TextField(blank=True, help_text='Description pour SEO')),
                ('posts_per_page', models.PositiveIntegerField(default=12, help_text='Articles par page')),
                ('posts_per_rss', models.PositiveIntegerField(default=20, help_text='Articles dans flux RSS')),
                ('excerpt_length', models.PositiveIntegerField(default=160, help_text='Longueur auto des extraits')),
                ('enable_comments', models.BooleanField(default=False)),
                ('enable_newsletter', models.BooleanField(default=True)),
                ('enable_related_posts', models.BooleanField(default=True)),
                ('enable_auto_publish', models.BooleanField(default=False, help_text='Publication automatique des articles programmés')),
                ('default_meta_title_pattern', models.CharField(default='{{article.title}} | {{blog.name}}', help_text='Pattern titre SEO', max_length=200)),
                ('default_meta_description_pattern', models.CharField(default='{{article.excerpt|truncate:150}}', help_text='Pattern description SEO', max_length=300)),
                ('google_analytics_id', models.CharField(blank=True, help_text='GA ID spécifique blog', max_length=50)),
                ('default_featured_image', models.URLField(blank=True, help_text='Image par défaut pour articles')),
                ('auto_generate_excerpts', models.BooleanField(default=True, help_text='Générer automatiquement les extraits')),
            ],
            options={
                'verbose_name': 'Configuration Blog',
                'verbose_name_plural': 'Configurations Blog',
                'db_table': 'blog_config_blogconfig',
            },
        ),
    ]
