# backend/seo_websites_categorization/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_websites_categorization', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seo_websites_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitecategorization',
            name='categorized_by',
            field=models.ForeignKey(blank=True, help_text='Utilisateur qui a fait la catégorisation', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='websitecategorization',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='websites', to='seo_websites_categorization.websitecategory'),
        ),
        migrations.AddField(
            model_name='websitecategorization',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorizations', to='seo_websites_core.website'),
        ),
        migrations.AddIndex(
            model_name='websitecategory',
            index=models.Index(fields=['parent', 'display_order'], name='seo_website_parent__292276_idx'),
        ),
        migrations.AddIndex(
            model_name='websitecategory',
            index=models.Index(fields=['slug'], name='seo_website_slug_4bcbd6_idx'),
        ),
        migrations.AddIndex(
            model_name='websitecategorization',
            index=models.Index(fields=['website', 'is_primary'], name='seo_website_website_ca40e7_idx'),
        ),
        migrations.AddIndex(
            model_name='websitecategorization',
            index=models.Index(fields=['category', 'is_primary'], name='seo_website_categor_5ba5fd_idx'),
        ),
        migrations.AddIndex(
            model_name='websitecategorization',
            index=models.Index(fields=['source'], name='seo_website_source_a13e4d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='websitecategorization',
            unique_together={('website', 'category')},
        ),
    ]
