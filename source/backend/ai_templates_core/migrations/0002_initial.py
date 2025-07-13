# backend/ai_templates_core/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brandtemplateconfig',
            name='brand',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='template_config', to='brands_core.brand'),
        ),
        migrations.AddField(
            model_name='basetemplate',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_templates', to='brands_core.brand'),
        ),
    ]
