# backend/blog_collections/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog_collections', '0001_initial'),
        ('blog_content', '0001_initial'),
        ('seo_pages_content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogcollectionitem',
            name='added_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='added_collection_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blogcollectionitem',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_items', to='blog_content.blogarticle'),
        ),
        migrations.AddField(
            model_name='blogcollectionitem',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_items', to='blog_collections.blogcollection'),
        ),
        migrations.AddField(
            model_name='blogcollection',
            name='articles',
            field=models.ManyToManyField(related_name='collections', through='blog_collections.BlogCollectionItem', to='blog_content.blogarticle'),
        ),
        migrations.AddField(
            model_name='blogcollection',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand'),
        ),
        migrations.AddField(
            model_name='blogcollection',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_collections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blogcollection',
            name='template_page',
            field=models.ForeignKey(blank=True, help_text='Template pour cette collection', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blog_collections', to='seo_pages_content.page'),
        ),
        migrations.AddIndex(
            model_name='blogcollectionitem',
            index=models.Index(fields=['collection', 'order'], name='blog_collec_collect_9007a5_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='blogcollectionitem',
            unique_together={('collection', 'article')},
        ),
        migrations.AddIndex(
            model_name='blogcollection',
            index=models.Index(fields=['brand', 'is_active'], name='blog_collec_brand_i_5d6677_idx'),
        ),
        migrations.AddIndex(
            model_name='blogcollection',
            index=models.Index(fields=['collection_type', 'is_active'], name='blog_collec_collect_e51a6b_idx'),
        ),
        migrations.AddIndex(
            model_name='blogcollection',
            index=models.Index(fields=['is_featured', 'created_at'], name='blog_collec_is_feat_ceb1de_idx'),
        ),
    ]
