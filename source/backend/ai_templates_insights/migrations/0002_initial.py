# backend/ai_templates_insights/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0002_initial'),
        ('ai_templates_insights', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templaterecommendation',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='template_recommendations', to='brands_core.brand'),
        ),
        migrations.AddField(
            model_name='templaterecommendation',
            name='recommended_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_templates_core.basetemplate'),
        ),
    ]
