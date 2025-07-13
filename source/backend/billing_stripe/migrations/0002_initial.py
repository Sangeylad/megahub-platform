# backend/billing_stripe/migrations/0002_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing_stripe', '0001_initial'),
        ('company_core', '0001_initial'),
        ('billing_core', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripepaymentmethod',
            name='company',
            field=models.ForeignKey(help_text='Entreprise propriétaire', on_delete=django.db.models.deletion.CASCADE, related_name='stripe_payment_methods', to='company_core.company'),
        ),
        migrations.AddField(
            model_name='stripeinvoice',
            name='invoice',
            field=models.OneToOneField(help_text='Facture locale liée', on_delete=django.db.models.deletion.CASCADE, related_name='stripe_invoice', to='billing_core.invoice'),
        ),
        migrations.AddField(
            model_name='stripecustomer',
            name='company',
            field=models.OneToOneField(help_text='Entreprise liée', on_delete=django.db.models.deletion.CASCADE, related_name='stripe_customer', to='company_core.company'),
        ),
        migrations.AddIndex(
            model_name='stripesubscription',
            index=models.Index(fields=['stripe_subscription_id'], name='stripe_subs_stripe__88078b_idx'),
        ),
        migrations.AddIndex(
            model_name='stripesubscription',
            index=models.Index(fields=['stripe_status'], name='stripe_subs_stripe__087ca4_idx'),
        ),
        migrations.AddIndex(
            model_name='stripepaymentmethod',
            index=models.Index(fields=['stripe_payment_method_id'], name='stripe_paym_stripe__b79ebe_idx'),
        ),
        migrations.AddIndex(
            model_name='stripepaymentmethod',
            index=models.Index(fields=['company', 'is_default'], name='stripe_paym_company_4f1ac8_idx'),
        ),
        migrations.AddIndex(
            model_name='stripeinvoice',
            index=models.Index(fields=['stripe_invoice_id'], name='stripe_invo_stripe__6e4e27_idx'),
        ),
        migrations.AddIndex(
            model_name='stripeinvoice',
            index=models.Index(fields=['stripe_status'], name='stripe_invo_stripe__8ea6b6_idx'),
        ),
        migrations.AddIndex(
            model_name='stripecustomer',
            index=models.Index(fields=['stripe_customer_id'], name='stripe_cust_stripe__5a6756_idx'),
        ),
    ]
