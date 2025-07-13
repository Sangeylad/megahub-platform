# backend/ai_templates_storage/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ai_templates_storage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templateversion',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authored_template_versions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templateversion',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='ai_templates_core.basetemplate'),
        ),
        migrations.AlterUniqueTogether(
            name='templatevariable',
            unique_together={('name',)},
        ),
        migrations.AddIndex(
            model_name='templateversion',
            index=models.Index(fields=['template', 'is_current'], name='template_ve_templat_26acea_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='templateversion',
            unique_together={('template', 'version_number')},
        ),
    ]
