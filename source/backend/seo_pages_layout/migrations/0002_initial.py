# backend/seo_pages_layout/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
        ('seo_pages_layout', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pagesection',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagesection',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='seo_pages_content.page'),
        ),
        migrations.AddField(
            model_name='pagesection',
            name='parent_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_sections', to='seo_pages_layout.pagesection'),
        ),
        migrations.AddField(
            model_name='pagelayout',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
        ),
        migrations.AddField(
            model_name='pagelayout',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='layout_config', to='seo_pages_content.page'),
        ),
        migrations.AddIndex(
            model_name='pagesection',
            index=models.Index(fields=['page', 'parent_section', 'order'], name='seo_pages_l_page_id_108462_idx'),
        ),
        migrations.AddIndex(
            model_name='pagesection',
            index=models.Index(fields=['order', 'created_at'], name='seo_pages_l_order_6f7ac9_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='pagesection',
            unique_together={('page', 'parent_section', 'order')},
        ),
        migrations.AddIndex(
            model_name='pagelayout',
            index=models.Index(fields=['page', 'render_strategy'], name='seo_pages_l_page_id_375a8c_idx'),
        ),
    ]
