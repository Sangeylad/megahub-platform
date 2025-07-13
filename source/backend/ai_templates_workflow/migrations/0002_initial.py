# backend/ai_templates_workflow/migrations/0002_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_workflow', '0001_initial'),
        ('ai_templates_core', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='templatevalidationresult',
            name='validated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templatevalidationresult',
            name='validation_rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_templates_workflow.templatevalidationrule'),
        ),
        migrations.AddField(
            model_name='templatereview',
            name='approval',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ai_templates_workflow.templateapproval'),
        ),
        migrations.AddField(
            model_name='templatereview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templateapproval',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_approvals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templateapproval',
            name='submitted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_approvals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='templateapproval',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='ai_templates_core.basetemplate'),
        ),
        migrations.AddIndex(
            model_name='templatevalidationresult',
            index=models.Index(fields=['template', 'is_valid'], name='template_va_templat_874436_idx'),
        ),
        migrations.AddIndex(
            model_name='templatevalidationresult',
            index=models.Index(fields=['validation_rule', 'created_at'], name='template_va_validat_e480bd_idx'),
        ),
        migrations.AddIndex(
            model_name='templateapproval',
            index=models.Index(fields=['template', 'status'], name='template_ap_templat_b3079d_idx'),
        ),
        migrations.AddIndex(
            model_name='templateapproval',
            index=models.Index(fields=['status', 'submitted_at'], name='template_ap_status_311c42_idx'),
        ),
    ]
