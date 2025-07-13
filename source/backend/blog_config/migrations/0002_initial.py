# backend/blog_config/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
        ('blog_config', '0001_initial'),
        ('seo_websites_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogconfig',
            name='template_archive_page',
            field=models.ForeignKey(blank=True, help_text='Page template pour archives', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blog_archive_templates', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='template_article_page',
            field=models.ForeignKey(blank=True, help_text='Page template pour articles', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blog_article_templates', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='template_category_page',
            field=models.ForeignKey(blank=True, help_text='Page template pour catégories', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blog_category_templates', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='website',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blog_config', to='seo_websites_core.website'),
        ),
    ]
