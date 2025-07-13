# backend/billing_stripe/webhooks/stripe_webhooks.py
import stripe
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from billing_stripe.services.stripe_service import StripeService
from billing_stripe.models.stripe_models import StripeWebhookEvent

# Configuration Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """
    Vue pour traiter les webhooks Stripe
    
    Endpoint: POST /stripe-webhooks/
    """
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            # Vérifier la signature du webhook
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            # Payload invalide
            return HttpResponse(
                'Invalid payload',
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError:
            # Signature invalide
            return HttpResponse(
                'Invalid signature',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Traiter l'événement
            webhook_event = StripeService.handle_webhook_event(event)
            
            return HttpResponse(
                f'Webhook processed: {webhook_event.id}',
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # Logger l'erreur
            print(f"Erreur webhook Stripe: {str(e)}")
            
            return HttpResponse(
                f'Webhook processing failed: {str(e)}',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def stripe_webhook_handler(request):
    """
    Handler alternatif pour les webhooks Stripe (DRF)
    
    Endpoint: POST /api/stripe-webhooks/
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Vérifier la signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return Response(
            {'error': 'Invalid payload'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.SignatureVerificationError:
        return Response(
            {'error': 'Invalid signature'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Traiter l'événement
        webhook_event = StripeService.handle_webhook_event(event)
        
        return Response({
            'message': 'Webhook processed successfully',
            'event_id': webhook_event.id,
            'event_type': webhook_event.event_type,
            'status': webhook_event.processing_status
        })
        
    except Exception as e:
        return Response(
            {'error': f'Webhook processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Handlers spécifiques pour chaque type d'événement
class StripeEventHandlers:
    """Handlers pour les différents types d'événements Stripe"""
    
    @staticmethod
    def handle_customer_created(event_data):
        """
        Traite la création d'un client
        """
        customer_data = event_data['data']['object']
        
        # Traitement spécifique
        print(f"Nouveau client créé: {customer_data['id']}")
        
        return True
    
    @staticmethod
    def handle_customer_updated(event_data):
        """
        Traite la mise à jour d'un client
        """
        customer_data = event_data['data']['object']
        
        # Synchroniser les données client
        try:
            from billing_stripe.models.stripe_models import StripeCustomer
            stripe_customer = StripeCustomer.objects.get(
                stripe_customer_id=customer_data['id']
            )
            
            # Mettre à jour les données
            stripe_customer.email = customer_data['email']
            stripe_customer.raw_data = customer_data
            stripe_customer.save()
            
            return True
            
        except StripeCustomer.DoesNotExist:
            print(f"Client Stripe non trouvé: {customer_data['id']}")
            return False
    
    @staticmethod
    def handle_invoice_payment_succeeded(event_data):
        """
        Traite le paiement réussi d'une facture
        """
        invoice_data = event_data['data']['object']
        
        try:
            from billing_stripe.models.stripe_models import StripeInvoice
            stripe_invoice = StripeInvoice.objects.get(
                stripe_invoice_id=invoice_data['id']
            )
            
            # Mettre à jour la facture locale
            invoice = stripe_invoice.invoice
            invoice.status = 'paid'
            invoice.paid_at = timezone.now()
            invoice.save()
            
            # Mettre à jour les données Stripe
            stripe_invoice.stripe_status = 'paid'
            stripe_invoice.stripe_paid_at = timezone.datetime.fromtimestamp(
                invoice_data['status_transitions']['paid_at'],
                tz=timezone.get_current_timezone()
            )
            stripe_invoice.save()
            
            return True
            
        except StripeInvoice.DoesNotExist:
            print(f"Facture Stripe non trouvée: {invoice_data['id']}")
            return False
    
    @staticmethod
    def handle_invoice_payment_failed(event_data):
        """
        Traite l'échec de paiement d'une facture
        """
        invoice_data = event_data['data']['object']
        
        try:
            from billing_stripe.models.stripe_models import StripeInvoice
            stripe_invoice = StripeInvoice.objects.get(
                stripe_invoice_id=invoice_data['id']
            )
            
            # Mettre à jour la facture locale
            invoice = stripe_invoice.invoice
            invoice.status = 'open'  # ou 'past_due'
            invoice.save()
            
            # Créer une alerte
            from billing_core.models.billing import UsageAlert
            UsageAlert.objects.create(
                company=invoice.company,
                alert_type='payment_failed',
                message=f"Échec de paiement pour la facture {invoice.invoice_number}",
                status='active'
            )
            
            return True
            
        except StripeInvoice.DoesNotExist:
            print(f"Facture Stripe non trouvée: {invoice_data['id']}")
            return False
    
    @staticmethod
    def handle_subscription_created(event_data):
        """
        Traite la création d'un abonnement
        """
        subscription_data = event_data['data']['object']
        
        # Traitement spécifique
        print(f"Nouvel abonnement créé: {subscription_data['id']}")
        
        return True
    
    @staticmethod
    def handle_subscription_updated(event_data):
        """
        Traite la mise à jour d'un abonnement
        """
        subscription_data = event_data['data']['object']
        
        try:
            from billing_stripe.models.stripe_models import StripeSubscription
            stripe_subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            
            # Synchroniser les données
            StripeService.sync_subscription(stripe_subscription.subscription)
            
            return True
            
        except StripeSubscription.DoesNotExist:
            print(f"Abonnement Stripe non trouvé: {subscription_data['id']}")
            return False
    
    @staticmethod
    def handle_subscription_deleted(event_data):
        """
        Traite la suppression d'un abonnement
        """
        subscription_data = event_data['data']['object']
        
        try:
            from billing_stripe.models.stripe_models import StripeSubscription
            stripe_subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            
            # Marquer l'abonnement comme annulé
            subscription = stripe_subscription.subscription
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            
            return True
            
        except StripeSubscription.DoesNotExist:
            print(f"Abonnement Stripe non trouvé: {subscription_data['id']}")
            return False
    
    @staticmethod
    def handle_payment_method_attached(event_data):
        """
        Traite l'ajout d'une méthode de paiement
        """
        payment_method_data = event_data['data']['object']
        
        # Traitement spécifique
        print(f"Méthode de paiement ajoutée: {payment_method_data['id']}")
        
        return True
    
    @staticmethod
    def handle_payment_intent_succeeded(event_data):
        """
        Traite le succès d'un paiement
        """
        payment_intent_data = event_data['data']['object']
        
        # Traitement spécifique
        print(f"Paiement réussi: {payment_intent_data['id']}")
        
        return True
    
    @staticmethod
    def handle_charge_dispute_created(event_data):
        """
        Traite la création d'un litige
        """
        dispute_data = event_data['data']['object']
        
        # Créer une alerte pour le litige
        try:
            charge_id = dispute_data['charge']
            
            from billing_core.models.billing import UsageAlert
            UsageAlert.objects.create(
                company=None,  # À déterminer selon la charge
                alert_type='dispute_created',
                message=f"Litige créé pour la charge {charge_id}",
                status='active'
            )
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du traitement du litige: {str(e)}")
            return False

# Mapping des événements vers leurs handlers
STRIPE_EVENT_HANDLERS = {
    'customer.created': StripeEventHandlers.handle_customer_created,
    'customer.updated': StripeEventHandlers.handle_customer_updated,
    'invoice.payment_succeeded': StripeEventHandlers.handle_invoice_payment_succeeded,
    'invoice.payment_failed': StripeEventHandlers.handle_invoice_payment_failed,
    'customer.subscription.created': StripeEventHandlers.handle_subscription_created,
    'customer.subscription.updated': StripeEventHandlers.handle_subscription_updated,
    'customer.subscription.deleted': StripeEventHandlers.handle_subscription_deleted,
    'payment_method.attached': StripeEventHandlers.handle_payment_method_attached,
    'payment_intent.succeeded': StripeEventHandlers.handle_payment_intent_succeeded,
    'charge.dispute.created': StripeEventHandlers.handle_charge_dispute_created,
}

def process_stripe_event(event_data):
    """
    Traite un événement Stripe selon son type
    """
    event_type = event_data['type']
    
    if event_type in STRIPE_EVENT_HANDLERS:
        handler = STRIPE_EVENT_HANDLERS[event_type]
        try:
            return handler(event_data)
        except Exception as e:
            print(f"Erreur dans le handler {event_type}: {str(e)}")
            return False
    else:
        print(f"Type d'événement non géré: {event_type}")
        return True  # Pas d'erreur, juste pas géré

# Utilitaires webhook
def validate_webhook_signature(payload, sig_header, secret):
    """
    Valide la signature d'un webhook Stripe
    """
    try:
        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except (ValueError, stripe.error.SignatureVerificationError):
        return False

def log_webhook_event(event_data, processing_status='processed', error_message=''):
    """
    Log un événement webhook
    """
    try:
        StripeWebhookEvent.objects.create(
            stripe_event_id=event_data['id'],
            event_type=event_data['type'],
            processing_status=processing_status,
            error_message=error_message,
            raw_event_data=event_data
        )
    except Exception as e:
        print(f"Erreur lors du log de l'événement: {str(e)}")

# Configuration des URLs webhook
def get_webhook_urls():
    """
    Retourne les URLs des webhooks configurés
    """
    from django.urls import reverse
    
    return {
        'webhook_url': reverse('stripe_webhook'),
        'webhook_api_url': reverse('stripe_webhook_api'),
    }
