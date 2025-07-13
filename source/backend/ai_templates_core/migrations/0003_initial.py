# backend/ai_templates_core/migrations/0003_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='basetemplate',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authored_ai_templates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='basetemplate',
            name='template_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to='ai_templates_core.templatetype'),
        ),
        migrations.AddIndex(
            model_name='basetemplate',
            index=models.Index(fields=['brand', 'template_type'], name='base_templa_brand_i_f31cf5_idx'),
        ),
        migrations.AddIndex(
            model_name='basetemplate',
            index=models.Index(fields=['is_active', 'is_public'], name='base_templa_is_acti_7ef937_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='basetemplate',
            unique_together={('brand', 'name', 'template_type')},
        ),
    ]
