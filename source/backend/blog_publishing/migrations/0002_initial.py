# backend/blog_publishing/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog_publishing', '0001_initial'),
        ('blog_content', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blogscheduledpublication',
            name='scheduled_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_publications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blogpublishingstatus',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_articles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blogpublishingstatus',
            name='article',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='publishing_status', to='blog_content.blogarticle'),
        ),
        migrations.AddIndex(
            model_name='blogpublishingstatus',
            index=models.Index(fields=['status', 'published_date'], name='blog_publis_status_9067e1_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpublishingstatus',
            index=models.Index(fields=['scheduled_date'], name='blog_publis_schedul_13422d_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpublishingstatus',
            index=models.Index(fields=['is_featured', 'published_date'], name='blog_publis_is_feat_b07266_idx'),
        ),
    ]
