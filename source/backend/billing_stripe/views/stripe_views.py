# backend/billing_stripe/views/stripe_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from billing_stripe.models.stripe_models import (
    StripeCustomer, StripeSubscription, StripeInvoice, 
    StripeWebhookEvent, StripePaymentMethod
)
from billing_stripe.serializers.stripe_serializers import (
    StripeCustomerSerializer, StripeSubscriptionSerializer, StripeInvoiceSerializer,
    StripeWebhookEventSerializer, StripeWebhookEventListSerializer, StripePaymentMethodSerializer,
    StripeCheckoutSessionSerializer, StripePaymentMethodCreateSerializer, StripeSyncSerializer
)
from billing_stripe.services.stripe_service import StripeService
from common.views.mixins import AnalyticsViewSetMixin

class StripeCustomerViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des clients Stripe
    
    Endpoints:
    - GET /stripe-customers/ - Liste des clients
    - GET /stripe-customers/{id}/ - Détail d'un client
    - POST /stripe-customers/{id}/sync/ - Synchroniser un client
    """
    
    queryset = StripeCustomer.objects.select_related('company').all()
    serializer_class = StripeCustomerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company']
    search_fields = ['company__name', 'email', 'stripe_customer_id']
    ordering_fields = ['stripe_created_at', 'last_sync_at']
    ordering = ['-stripe_created_at']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin ne voit que son entreprise
        if user.is_company_admin():
            return queryset.filter(company=user.company)
        
        # Autres utilisateurs ne voient que leur entreprise
        if user.company:
            return queryset.filter(company=user.company)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        POST /stripe-customers/{id}/sync/
        
        Synchronise un client avec Stripe
        """
        stripe_customer = self.get_object()
        
        try:
            updated_customer = StripeService.sync_customer(stripe_customer.company)
            
            return Response({
                'message': 'Client synchronisé avec succès',
                'customer_id': updated_customer.id,
                'last_sync_at': updated_customer.last_sync_at
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la synchronisation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StripeSubscriptionViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des abonnements Stripe
    
    Endpoints:
    - GET /stripe-subscriptions/ - Liste des abonnements
    - GET /stripe-subscriptions/{id}/ - Détail d'un abonnement
    - POST /stripe-subscriptions/{id}/sync/ - Synchroniser un abonnement
    """
    
    queryset = StripeSubscription.objects.select_related('subscription__company').all()
    serializer_class = StripeSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['subscription__company', 'stripe_status']
    search_fields = ['subscription__company__name', 'stripe_subscription_id']
    ordering_fields = ['stripe_current_period_start', 'last_sync_at']
    ordering = ['-stripe_current_period_start']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin ne voit que son entreprise
        if user.is_company_admin():
            return queryset.filter(subscription__company=user.company)
        
        # Autres utilisateurs ne voient que leur entreprise
        if user.company:
            return queryset.filter(subscription__company=user.company)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        POST /stripe-subscriptions/{id}/sync/
        
        Synchronise un abonnement avec Stripe
        """
        stripe_subscription = self.get_object()
        
        try:
            updated_subscription = StripeService.sync_subscription(stripe_subscription.subscription)
            
            return Response({
                'message': 'Abonnement synchronisé avec succès',
                'subscription_id': updated_subscription.id,
                'status': updated_subscription.status
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la synchronisation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StripeInvoiceViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des factures Stripe
    
    Endpoints:
    - GET /stripe-invoices/ - Liste des factures
    - GET /stripe-invoices/{id}/ - Détail d'une facture
    """
    
    queryset = StripeInvoice.objects.select_related('invoice__company').all()
    serializer_class = StripeInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['invoice__company', 'stripe_status']
    search_fields = ['invoice__company__name', 'stripe_invoice_id']
    ordering_fields = ['stripe_created_at', 'stripe_paid_at']
    ordering = ['-stripe_created_at']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin ne voit que son entreprise
        if user.is_company_admin():
            return queryset.filter(invoice__company=user.company)
        
        # Autres utilisateurs ne voient que leur entreprise
        if user.company:
            return queryset.filter(invoice__company=user.company)
        
        return queryset.none()

class StripePaymentMethodViewSet(AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des méthodes de paiement Stripe
    
    Endpoints:
    - GET /stripe-payment-methods/ - Liste des méthodes
    - POST /stripe-payment-methods/ - Ajouter une méthode
    - GET /stripe-payment-methods/{id}/ - Détail d'une méthode
    - DELETE /stripe-payment-methods/{id}/ - Supprimer une méthode
    - POST /stripe-payment-methods/{id}/set-default/ - Définir par défaut
    """
    
    queryset = StripePaymentMethod.objects.select_related('company').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'payment_type', 'is_default', 'is_active']
    search_fields = ['company__name', 'card_brand', 'card_last4']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'create':
            return StripePaymentMethodCreateSerializer
        return StripePaymentMethodSerializer
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin ne voit que son entreprise
        if user.is_company_admin():
            return queryset.filter(company=user.company)
        
        # Autres utilisateurs ne voient que leur entreprise
        if user.company:
            return queryset.filter(company=user.company)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        POST /stripe-payment-methods/{id}/set-default/
        
        Définit une méthode de paiement par défaut
        """
        payment_method = self.get_object()
        
        try:
            updated_method = StripeService.set_default_payment_method(
                payment_method.company,
                payment_method.stripe_payment_method_id
            )
            
            return Response({
                'message': 'Méthode de paiement définie par défaut',
                'payment_method_id': updated_method.id,
                'display_name': updated_method.get_display_name()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la définition par défaut: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_destroy(self, instance):
        """Suppression avec détachement Stripe"""
        try:
            # Détacher de Stripe
            import stripe
            stripe.PaymentMethod.detach(instance.stripe_payment_method_id)
            
            # Supprimer localement
            super().perform_destroy(instance)
            
        except Exception as e:
            # Supprimer localement même si erreur Stripe
            super().perform_destroy(instance)

class StripeWebhookEventViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des événements webhook
    
    Endpoints:
    - GET /stripe-webhook-events/ - Liste des événements
    - GET /stripe-webhook-events/{id}/ - Détail d'un événement
    - POST /stripe-webhook-events/{id}/retry/ - Retraiter un événement
    """
    
    queryset = StripeWebhookEvent.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['event_type', 'processing_status']
    search_fields = ['stripe_event_id', 'event_type']
    ordering_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return StripeWebhookEventListSerializer
        return StripeWebhookEventSerializer
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur (admin seulement)"""
        if not self.request.user.is_superuser:
            return self.queryset.none()
        return super().get_queryset()
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """
        POST /stripe-webhook-events/{id}/retry/
        
        Retraite un événement webhook échoué
        """
        webhook_event = self.get_object()
        
        if not webhook_event.can_retry():
            return Response(
                {'error': 'Événement ne peut pas être retraité'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Retraiter l'événement
            processed_event = StripeService.handle_webhook_event(webhook_event.raw_event_data)
            
            return Response({
                'message': 'Événement retraité avec succès',
                'event_id': processed_event.id,
                'status': processed_event.processing_status
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du retraitement: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def failed_events(self, request):
        """
        GET /stripe-webhook-events/failed-events/
        
        Événements échoués
        """
        failed_events = self.get_queryset().filter(processing_status='failed')
        
        return Response({
            'failed_events_count': failed_events.count(),
            'failed_events': StripeWebhookEventListSerializer(failed_events, many=True).data
        })

class StripeCheckoutViewSet(viewsets.ViewSet):
    """
    ViewSet pour la gestion des sessions de checkout Stripe
    
    Endpoints:
    - POST /stripe-checkout/create-session/ - Créer une session
    - GET /stripe-checkout/portal-url/ - URL du portail client
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """
        POST /stripe-checkout/create-session/
        
        Crée une session de checkout Stripe
        """
        serializer = StripeCheckoutSessionSerializer(data=request.data)
        
        if serializer.is_valid():
            session_data = serializer.save()
            return Response(session_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def portal_url(self, request):
        """
        GET /stripe-checkout/portal-url/
        
        Génère l'URL du portail client Stripe
        """
        user = request.user
        
        if not user.company or not user.company.stripe_customer_id:
            return Response(
                {'error': 'Entreprise sans client Stripe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            portal_url = StripeService.get_billing_portal_url(user.company)
            
            return Response({
                'portal_url': portal_url,
                'company': user.company.name
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du portail: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StripeSyncViewSet(viewsets.ViewSet):
    """
    ViewSet pour la synchronisation avec Stripe
    
    Endpoints:
    - POST /stripe-sync/sync/ - Synchroniser les données
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        POST /stripe-sync/sync/
        
        Synchronise les données avec Stripe
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StripeSyncSerializer(data=request.data)
        
        if serializer.is_valid():
            results = serializer.sync()
            return Response({
                'message': 'Synchronisation terminée',
                'results': results
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
