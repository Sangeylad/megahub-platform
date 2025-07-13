# backend/billing_stripe/services/stripe_service.py
import stripe
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from billing_stripe.models.stripe_models import (
    StripeCustomer, StripeSubscription, StripeInvoice, 
    StripeWebhookEvent, StripePaymentMethod
)
from billing_core.services.billing_service import BillingService

# Configuration Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class StripeService:
    """Service pour l'intégration Stripe"""
    
    @staticmethod
    def create_customer(company):
        """Crée un client Stripe"""
        try:
            # Créer le client côté Stripe
            stripe_customer = stripe.Customer.create(
                email=company.billing_email,
                name=company.name,
                metadata={
                    'company_id': company.id,
                    'company_name': company.name,
                }
            )
            
            # Sauvegarder localement
            customer = StripeCustomer.objects.create(
                company=company,
                stripe_customer_id=stripe_customer.id,
                email=stripe_customer.email,
                stripe_created_at=timezone.datetime.fromtimestamp(
                    stripe_customer.created, 
                    tz=timezone.get_current_timezone()
                ),
                raw_data=stripe_customer
            )
            
            # Mettre à jour la company
            company.stripe_customer_id = stripe_customer.id
            company.save(update_fields=['stripe_customer_id'])
            
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la création du client: {str(e)}")
    
    @staticmethod
    def create_subscription(company, plan, payment_method_id=None, trial_days=None):
        """Crée un abonnement Stripe"""
        try:
            # Vérifier/créer le client Stripe
            if not company.stripe_customer_id:
                stripe_customer = StripeService.create_customer(company)
            else:
                stripe_customer = company.stripe_customer
            
            # Paramètres de l'abonnement
            subscription_params = {
                'customer': stripe_customer.stripe_customer_id,
                'items': [{'price': plan.stripe_price_id}],
                'metadata': {
                    'company_id': company.id,
                    'plan_id': plan.id,
                }
            }
            
            # Méthode de paiement
            if payment_method_id:
                subscription_params['default_payment_method'] = payment_method_id
            
            # Période d'essai
            if trial_days:
                subscription_params['trial_period_days'] = trial_days
            
            # Créer l'abonnement côté Stripe
            stripe_subscription = stripe.Subscription.create(**subscription_params)
            
            # Créer l'abonnement local
            local_subscription = BillingService.create_subscription(
                company=company,
                plan=plan,
                trial_days=trial_days
            )
            
            # Sauvegarder les données Stripe
            StripeSubscription.objects.create(
                subscription=local_subscription,
                stripe_subscription_id=stripe_subscription.id,
                stripe_status=stripe_subscription.status,
                stripe_current_period_start=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start,
                    tz=timezone.get_current_timezone()
                ),
                stripe_current_period_end=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end,
                    tz=timezone.get_current_timezone()
                ),
                stripe_trial_end=timezone.datetime.fromtimestamp(
                    stripe_subscription.trial_end,
                    tz=timezone.get_current_timezone()
                ) if stripe_subscription.trial_end else None,
                raw_data=stripe_subscription
            )
            
            # Mettre à jour l'abonnement local avec l'ID Stripe
            local_subscription.stripe_subscription_id = stripe_subscription.id
            local_subscription.save(update_fields=['stripe_subscription_id'])
            
            return local_subscription
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la création de l'abonnement: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription):
        """Annule un abonnement Stripe"""
        try:
            stripe_subscription = subscription.stripe_subscription
            
            # Annuler côté Stripe
            stripe.Subscription.delete(stripe_subscription.stripe_subscription_id)
            
            # Annuler localement
            BillingService.cancel_subscription(subscription)
            
            # Mettre à jour les données Stripe
            stripe_subscription.stripe_status = 'canceled'
            stripe_subscription.save(update_fields=['stripe_status'])
            
            return subscription
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de l'annulation: {str(e)}")
    
    @staticmethod
    def update_subscription(subscription, new_plan):
        """Met à jour un abonnement Stripe"""
        try:
            stripe_subscription = subscription.stripe_subscription
            
            # Mettre à jour côté Stripe
            stripe.Subscription.modify(
                stripe_subscription.stripe_subscription_id,
                items=[{
                    'id': stripe_subscription.raw_data['items']['data'][0]['id'],
                    'price': new_plan.stripe_price_id,
                }]
            )
            
            # Mettre à jour localement
            BillingService.upgrade_subscription(subscription, new_plan)
            
            return subscription
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la mise à jour: {str(e)}")
    
    @staticmethod
    def add_payment_method(company, payment_method_id):
        """Ajoute une méthode de paiement"""
        try:
            # Attacher la méthode de paiement au client
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=company.stripe_customer_id
            )
            
            # Récupérer les détails
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Sauvegarder localement
            local_payment_method = StripePaymentMethod.objects.create(
                company=company,
                stripe_payment_method_id=payment_method.id,
                payment_type=payment_method.type,
                raw_data=payment_method
            )
            
            # Remplir les détails selon le type
            if payment_method.type == 'card':
                card = payment_method.card
                local_payment_method.card_brand = card.brand
                local_payment_method.card_last4 = card.last4
                local_payment_method.card_exp_month = card.exp_month
                local_payment_method.card_exp_year = card.exp_year
                local_payment_method.save()
            
            return local_payment_method
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de l'ajout de la méthode de paiement: {str(e)}")
    
    @staticmethod
    def set_default_payment_method(company, payment_method_id):
        """Définit la méthode de paiement par défaut"""
        try:
            # Mettre à jour côté Stripe
            stripe.Customer.modify(
                company.stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Mettre à jour localement
            company.stripe_payment_methods.update(is_default=False)
            payment_method = company.stripe_payment_methods.get(
                stripe_payment_method_id=payment_method_id
            )
            payment_method.is_default = True
            payment_method.save(update_fields=['is_default'])
            
            return payment_method
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la définition de la méthode par défaut: {str(e)}")
    
    @staticmethod
    def sync_customer(company):
        """Synchronise un client avec Stripe"""
        try:
            if not company.stripe_customer_id:
                return None
            
            # Récupérer les données Stripe
            stripe_customer_data = stripe.Customer.retrieve(company.stripe_customer_id)
            
            # Mettre à jour les données locales
            stripe_customer = company.stripe_customer
            stripe_customer.email = stripe_customer_data.email
            stripe_customer.raw_data = stripe_customer_data
            stripe_customer.save()
            
            return stripe_customer
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la synchronisation: {str(e)}")
    
    @staticmethod
    def sync_subscription(subscription):
        """Synchronise un abonnement avec Stripe"""
        try:
            stripe_subscription = subscription.stripe_subscription
            
            # Récupérer les données Stripe
            stripe_data = stripe.Subscription.retrieve(
                stripe_subscription.stripe_subscription_id
            )
            
            # Mettre à jour les données locales
            stripe_subscription.stripe_status = stripe_data.status
            stripe_subscription.stripe_current_period_start = timezone.datetime.fromtimestamp(
                stripe_data.current_period_start,
                tz=timezone.get_current_timezone()
            )
            stripe_subscription.stripe_current_period_end = timezone.datetime.fromtimestamp(
                stripe_data.current_period_end,
                tz=timezone.get_current_timezone()
            )
            stripe_subscription.raw_data = stripe_data
            stripe_subscription.save()
            
            # Mettre à jour l'abonnement local
            subscription.status = StripeService.convert_stripe_status(stripe_data.status)
            subscription.current_period_start = stripe_subscription.stripe_current_period_start
            subscription.current_period_end = stripe_subscription.stripe_current_period_end
            subscription.save()
            
            return subscription
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur Stripe lors de la synchronisation de l'abonnement: {str(e)}")
    
    @staticmethod
    def convert_stripe_status(stripe_status):
        """Convertit un statut Stripe en statut local"""
        status_mapping = {
            'active': 'active',
            'trialing': 'trialing',
            'past_due': 'past_due',
            'canceled': 'canceled',
            'unpaid': 'unpaid',
        }
        return status_mapping.get(stripe_status, 'active')
    
    @staticmethod
    def handle_webhook_event(event_data):
        """Traite un événement webhook Stripe"""
        try:
            # Sauvegarder l'événement
            webhook_event = StripeWebhookEvent.objects.create(
                stripe_event_id=event_data['id'],
                event_type=event_data['type'],
                raw_event_data=event_data
            )
            
            # Traiter selon le type d'événement
            if event_data['type'] == 'invoice.payment_succeeded':
                StripeService.handle_payment_succeeded(event_data)
            elif event_data['type'] == 'invoice.payment_failed':
                StripeService.handle_payment_failed(event_data)
            elif event_data['type'] == 'customer.subscription.updated':
                StripeService.handle_subscription_updated(event_data)
            elif event_data['type'] == 'customer.subscription.deleted':
                StripeService.handle_subscription_canceled(event_data)
            
            webhook_event.mark_as_processed()
            return webhook_event
            
        except Exception as e:
            webhook_event.mark_as_failed(str(e))
            raise
    
    @staticmethod
    def handle_payment_succeeded(event_data):
        """Traite un paiement réussi"""
        invoice_data = event_data['data']['object']
        
        # Trouver la facture locale
        try:
            stripe_invoice = StripeInvoice.objects.get(
                stripe_invoice_id=invoice_data['id']
            )
            invoice = stripe_invoice.invoice
            
            # Mettre à jour le statut
            invoice.status = 'paid'
            invoice.paid_at = timezone.now()
            invoice.save()
            
        except StripeInvoice.DoesNotExist:
            # Créer la facture si elle n'existe pas
            pass
    
    @staticmethod
    def handle_payment_failed(event_data):
        """Traite un paiement échoué"""
        invoice_data = event_data['data']['object']
        
        # Logique de traitement des paiements échoués
        # Notifications, retry, etc.
        pass
    
    @staticmethod
    def handle_subscription_updated(event_data):
        """Traite une mise à jour d'abonnement"""
        subscription_data = event_data['data']['object']
        
        try:
            stripe_subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription = stripe_subscription.subscription
            
            # Synchroniser les données
            StripeService.sync_subscription(subscription)
            
        except StripeSubscription.DoesNotExist:
            pass
    
    @staticmethod
    def handle_subscription_canceled(event_data):
        """Traite une annulation d'abonnement"""
        subscription_data = event_data['data']['object']
        
        try:
            stripe_subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription = stripe_subscription.subscription
            
            # Marquer comme annulé
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            
        except StripeSubscription.DoesNotExist:
            pass
    
    @staticmethod
    def get_billing_portal_url(company):
        """Génère l'URL du portail de facturation Stripe"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=company.stripe_customer_id,
                return_url=settings.BILLING_PORTAL_RETURN_URL
            )
            return session.url
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de la génération du portail: {str(e)}")
    
    @staticmethod
    def create_checkout_session(company, plan, success_url, cancel_url):
        """Crée une session de checkout Stripe"""
        try:
            session = stripe.checkout.Session.create(
                customer=company.stripe_customer_id if company.stripe_customer_id else None,
                customer_email=company.billing_email if not company.stripe_customer_id else None,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'company_id': company.id,
                    'plan_id': plan.id,
                }
            )
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de la création de la session: {str(e)}")
