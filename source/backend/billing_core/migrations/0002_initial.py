# backend/billing_core/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing_core', '0001_initial'),
        ('company_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagealert',
            name='company',
            field=models.ForeignKey(help_text='Entreprise concernée', on_delete=django.db.models.deletion.CASCADE, related_name='usage_alerts', to='company_core.company'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='company',
            field=models.OneToOneField(help_text='Entreprise abonnée', on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='company_core.company'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(help_text='Plan souscrit', on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='billing_core.plan'),
        ),
        migrations.AddIndex(
            model_name='plan',
            index=models.Index(fields=['is_active'], name='plan_is_acti_dc0a05_idx'),
        ),
        migrations.AddIndex(
            model_name='plan',
            index=models.Index(fields=['plan_type'], name='plan_plan_ty_f5de88_idx'),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(help_text='Facture', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='billing_core.invoice'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='company',
            field=models.ForeignKey(help_text='Entreprise facturée', on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='company_core.company'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='subscription',
            field=models.ForeignKey(help_text='Abonnement facturé', on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='billing_core.subscription'),
        ),
        migrations.AddIndex(
            model_name='usagealert',
            index=models.Index(fields=['status'], name='usage_alert_status_e99e83_idx'),
        ),
        migrations.AddIndex(
            model_name='usagealert',
            index=models.Index(fields=['alert_type'], name='usage_alert_alert_t_4a2905_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['status'], name='subscriptio_status_3f9fd1_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['current_period_end'], name='subscriptio_current_d9fad5_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['status'], name='invoice_status_25ea8f_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['due_date'], name='invoice_due_dat_ee8b9c_idx'),
        ),
    ]
