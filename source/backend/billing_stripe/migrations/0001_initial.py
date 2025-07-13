# backend/billing_stripe/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_customer_id', models.CharField(help_text='ID client Stripe', max_length=255, unique=True)),
                ('email', models.EmailField(help_text='Email du client Stripe', max_length=254)),
                ('stripe_created_at', models.DateTimeField(help_text='Date de création côté Stripe')),
                ('last_sync_at', models.DateTimeField(auto_now=True, help_text='Dernière synchronisation')),
                ('raw_data', models.JSONField(blank=True, default=dict, help_text='Données brutes Stripe')),
            ],
            options={
                'db_table': 'stripe_customer',
            },
        ),
        migrations.CreateModel(
            name='StripeInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_invoice_id', models.CharField(help_text='ID facture Stripe', max_length=255, unique=True)),
                ('stripe_status', models.CharField(help_text='Statut Stripe', max_length=50)),
                ('stripe_subtotal', models.DecimalField(decimal_places=2, help_text='Sous-total Stripe', max_digits=10)),
                ('stripe_tax', models.DecimalField(decimal_places=2, help_text='Taxes Stripe', max_digits=10)),
                ('stripe_total', models.DecimalField(decimal_places=2, help_text='Total Stripe', max_digits=10)),
                ('stripe_payment_intent_id', models.CharField(blank=True, help_text='ID PaymentIntent Stripe', max_length=255)),
                ('stripe_charge_id', models.CharField(blank=True, help_text='ID Charge Stripe', max_length=255)),
                ('stripe_created_at', models.DateTimeField(help_text='Date création Stripe')),
                ('stripe_paid_at', models.DateTimeField(blank=True, help_text='Date paiement Stripe', null=True)),
                ('last_sync_at', models.DateTimeField(auto_now=True, help_text='Dernière synchronisation')),
                ('raw_data', models.JSONField(blank=True, default=dict, help_text='Données brutes Stripe')),
            ],
            options={
                'db_table': 'stripe_invoice',
            },
        ),
        migrations.CreateModel(
            name='StripePaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_payment_method_id', models.CharField(help_text='ID méthode de paiement Stripe', max_length=255, unique=True)),
                ('payment_type', models.CharField(choices=[('card', 'Carte'), ('sepa_debit', 'Prélèvement SEPA'), ('paypal', 'PayPal')], help_text='Type de paiement', max_length=20)),
                ('card_brand', models.CharField(blank=True, help_text='Marque de carte', max_length=20)),
                ('card_last4', models.CharField(blank=True, help_text='4 derniers chiffres', max_length=4)),
                ('card_exp_month', models.IntegerField(blank=True, help_text="Mois d'expiration", null=True)),
                ('card_exp_year', models.IntegerField(blank=True, help_text="Année d'expiration", null=True)),
                ('is_default', models.BooleanField(default=False, help_text='Méthode de paiement par défaut')),
                ('is_active', models.BooleanField(default=True, help_text='Méthode de paiement active')),
                ('raw_data', models.JSONField(blank=True, default=dict, help_text='Données brutes Stripe')),
            ],
            options={
                'db_table': 'stripe_payment_method',
            },
        ),
        migrations.CreateModel(
            name='StripeWebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_event_id', models.CharField(help_text='ID événement Stripe', max_length=255, unique=True)),
                ('event_type', models.CharField(choices=[('customer.created', 'Client créé'), ('customer.updated', 'Client mis à jour'), ('customer.deleted', 'Client supprimé'), ('invoice.created', 'Facture créée'), ('invoice.payment_succeeded', 'Paiement réussi'), ('invoice.payment_failed', 'Paiement échoué'), ('customer.subscription.created', 'Abonnement créé'), ('customer.subscription.updated', 'Abonnement mis à jour'), ('customer.subscription.deleted', 'Abonnement supprimé')], help_text="Type d'événement", max_length=50)),
                ('processing_status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En traitement'), ('processed', 'Traité'), ('failed', 'Échec'), ('ignored', 'Ignoré')], default='pending', help_text='Statut de traitement', max_length=20)),
                ('processed_at', models.DateTimeField(blank=True, help_text='Date de traitement', null=True)),
                ('error_message', models.TextField(blank=True, help_text="Message d'erreur si échec")),
                ('retry_count', models.IntegerField(default=0, help_text='Nombre de tentatives')),
                ('raw_event_data', models.JSONField(help_text="Données brutes de l'événement")),
            ],
            options={
                'db_table': 'stripe_webhook_event',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['stripe_event_id'], name='stripe_webh_stripe__f8a011_idx'), models.Index(fields=['event_type'], name='stripe_webh_event_t_71c571_idx'), models.Index(fields=['processing_status'], name='stripe_webh_process_abc1ef_idx')],
            },
        ),
        migrations.CreateModel(
            name='StripeSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_subscription_id', models.CharField(help_text='ID abonnement Stripe', max_length=255, unique=True)),
                ('stripe_status', models.CharField(help_text='Statut Stripe', max_length=50)),
                ('stripe_current_period_start', models.DateTimeField(help_text='Début période actuelle Stripe')),
                ('stripe_current_period_end', models.DateTimeField(help_text='Fin période actuelle Stripe')),
                ('stripe_trial_end', models.DateTimeField(blank=True, help_text="Fin d'essai Stripe", null=True)),
                ('last_sync_at', models.DateTimeField(auto_now=True, help_text='Dernière synchronisation')),
                ('raw_data', models.JSONField(blank=True, default=dict, help_text='Données brutes Stripe')),
                ('subscription', models.OneToOneField(help_text='Abonnement local lié', on_delete=django.db.models.deletion.CASCADE, related_name='stripe_subscription', to='billing_core.subscription')),
            ],
            options={
                'db_table': 'stripe_subscription',
            },
        ),
    ]
