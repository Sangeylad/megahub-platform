# backend/ai_core/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aijob',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand'),
        ),
    ]
