# backend/ai_providers/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company_core', '0001_initial'),
        ('ai_providers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiquota',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company_core.company'),
        ),
        migrations.AddField(
            model_name='aiquota',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_providers.aiprovider'),
        ),
        migrations.AddField(
            model_name='aicredentials',
            name='company',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_credentials', to='company_core.company'),
        ),
        migrations.AlterUniqueTogether(
            name='aiquota',
            unique_together={('company', 'provider')},
        ),
    ]
