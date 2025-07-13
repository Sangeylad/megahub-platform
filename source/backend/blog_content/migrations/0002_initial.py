# backend/blog_content/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog_content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogauthor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blog_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blogarticle',
            name='co_authors',
            field=models.ManyToManyField(blank=True, related_name='co_authored_articles', to='blog_content.blogauthor'),
        ),
        migrations.AddField(
            model_name='blogarticle',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blog_article', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='blogarticle',
            name='primary_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='blog_articles', to='blog_content.blogauthor'),
        ),
        migrations.AddField(
            model_name='blogarticle',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='blog_articles', to='blog_content.blogtag'),
        ),
        migrations.AddIndex(
            model_name='blogarticle',
            index=models.Index(fields=['primary_author', 'created_at'], name='blog_conten_primary_ee439f_idx'),
        ),
    ]
