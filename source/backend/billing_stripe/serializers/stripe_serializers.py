# backend/billing_stripe/serializers/stripe_serializers.py
from rest_framework import serializers
from billing_stripe.models.stripe_models import (
    StripeCustomer, StripeSubscription, StripeInvoice, 
    StripeWebhookEvent, StripePaymentMethod
)

class StripeCustomerSerializer(serializers.ModelSerializer):
    """Serializer pour StripeCustomer"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = StripeCustomer
        fields = [
            'id', 'company', 'company_name', 'stripe_customer_id', 'email',
            'stripe_created_at', 'last_sync_at', 'sync_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['stripe_created_at', 'last_sync_at', 'created_at', 'updated_at']
    
    def get_sync_status(self, obj):
        """Statut de synchronisation"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Considérer comme à jour si sync dans la dernière heure
        if obj.last_sync_at:
            time_diff = timezone.now() - obj.last_sync_at
            if time_diff < timedelta(hours=1):
                return 'up_to_date'
            elif time_diff < timedelta(days=1):
                return 'recent'
            else:
                return 'outdated'
        return 'never_synced'

class StripeSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour StripeSubscription"""
    
    # Informations de l'abonnement local
    company_name = serializers.CharField(source='subscription.company.name', read_only=True)
    plan_name = serializers.CharField(source='subscription.plan.display_name', read_only=True)
    local_status = serializers.CharField(source='subscription.status', read_only=True)
    
    # Comparaison statuts
    status_sync = serializers.SerializerMethodField()
    
    class Meta:
        model = StripeSubscription
        fields = [
            'id', 'subscription', 'company_name', 'plan_name',
            'stripe_subscription_id', 'stripe_status', 'local_status',
            'stripe_current_period_start', 'stripe_current_period_end',
            'stripe_trial_end', 'status_sync', 'last_sync_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['last_sync_at', 'created_at', 'updated_at']
    
    def get_status_sync(self, obj):
        """Vérifie la synchronisation des statuts"""
        from billing_stripe.services.stripe_service import StripeService
        local_status = obj.subscription.status
        stripe_status = StripeService.convert_stripe_status(obj.stripe_status)
        
        return {
            'is_synced': local_status == stripe_status,
            'local_status': local_status,
            'stripe_status': stripe_status,
            'last_sync': obj.last_sync_at,
        }

class StripeInvoiceSerializer(serializers.ModelSerializer):
    """Serializer pour StripeInvoice"""
    
    # Informations de la facture locale
    company_name = serializers.CharField(source='invoice.company.name', read_only=True)
    local_status = serializers.CharField(source='invoice.status', read_only=True)
    local_total = serializers.DecimalField(source='invoice.total', max_digits=10, decimal_places=2, read_only=True)
    
    # Comparaison données
    data_sync = serializers.SerializerMethodField()
    
    class Meta:
        model = StripeInvoice
        fields = [
            'id', 'invoice', 'company_name', 'stripe_invoice_id',
            'stripe_status', 'local_status', 'stripe_total', 'local_total',
            'stripe_subtotal', 'stripe_tax', 'stripe_payment_intent_id',
            'stripe_created_at', 'stripe_paid_at', 'data_sync', 'last_sync_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['last_sync_at', 'created_at', 'updated_at']
    
    def get_data_sync(self, obj):
        """Vérifie la synchronisation des données"""
        return {
            'total_synced': obj.invoice.total == obj.stripe_total,
            'status_synced': obj.invoice.status == obj.stripe_status.replace('open', 'open').replace('paid', 'paid'),
            'last_sync': obj.last_sync_at,
        }

class StripeWebhookEventSerializer(serializers.ModelSerializer):
    """Serializer pour StripeWebhookEvent"""
    
    can_retry = serializers.SerializerMethodField()
    
    class Meta:
        model = StripeWebhookEvent
        fields = [
            'id', 'stripe_event_id', 'event_type', 'processing_status',
            'processed_at', 'error_message', 'retry_count', 'can_retry',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['processed_at', 'created_at', 'updated_at']
    
    def get_can_retry(self, obj):
        """Vérifie si l'événement peut être retraité"""
        return obj.can_retry()

class StripePaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer pour StripePaymentMethod"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    display_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = StripePaymentMethod
        fields = [
            'id', 'company', 'company_name', 'stripe_payment_method_id',
            'payment_type', 'card_brand', 'card_last4', 'card_exp_month',
            'card_exp_year', 'is_default', 'is_active', 'display_name',
            'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Nom d'affichage de la méthode de paiement"""
        return obj.get_display_name()
    
    def get_is_expired(self, obj):
        """Vérifie si la carte est expirée"""
        return obj.is_card_expired()

class StripeWebhookEventListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes d'événements webhook"""
    
    processing_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = StripeWebhookEvent
        fields = [
            'id', 'stripe_event_id', 'event_type', 'processing_status',
            'retry_count', 'processing_duration', 'created_at'
        ]
    
    def get_processing_duration(self, obj):
        """Durée de traitement de l'événement"""
        if obj.processed_at:
            duration = obj.processed_at - obj.created_at
            return duration.total_seconds()
        return None

class StripeCheckoutSessionSerializer(serializers.Serializer):
    """Serializer pour créer une session de checkout Stripe"""
    
    company_id = serializers.IntegerField()
    plan_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    
    def validate_company_id(self, value):
        """Valide l'ID de l'entreprise"""
        from company_core.models.company import Company
        
        try:
            company = Company.objects.get(id=value)
            return value
        except Company.DoesNotExist:
            raise serializers.ValidationError("Entreprise non trouvée")
    
    def validate_plan_id(self, value):
        """Valide l'ID du plan"""
        from billing_core.models.billing import Plan
        
        try:
            plan = Plan.objects.get(id=value, is_active=True)
            if not plan.stripe_price_id:
                raise serializers.ValidationError("Ce plan n'a pas de prix Stripe configuré")
            return value
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan non trouvé ou inactif")
    
    def create(self, validated_data):
        """Crée une session de checkout"""
        from company_core.models.company import Company
        from billing_core.models.billing import Plan
        from billing_stripe.services.stripe_service import StripeService
        
        company = Company.objects.get(id=validated_data['company_id'])
        plan = Plan.objects.get(id=validated_data['plan_id'])
        
        session = StripeService.create_checkout_session(
            company=company,
            plan=plan,
            success_url=validated_data['success_url'],
            cancel_url=validated_data['cancel_url']
        )
        
        return {
            'session_id': session.id,
            'session_url': session.url,
            'checkout_url': session.url,
        }

class StripePaymentMethodCreateSerializer(serializers.Serializer):
    """Serializer pour ajouter une méthode de paiement"""
    
    company_id = serializers.IntegerField()
    payment_method_id = serializers.CharField()
    set_as_default = serializers.BooleanField(default=False)
    
    def validate_company_id(self, value):
        """Valide l'ID de l'entreprise"""
        from company_core.models.company import Company
        
        try:
            company = Company.objects.get(id=value)
            if not company.stripe_customer_id:
                raise serializers.ValidationError("Cette entreprise n'a pas de client Stripe")
            return value
        except Company.DoesNotExist:
            raise serializers.ValidationError("Entreprise non trouvée")
    
    def create(self, validated_data):
        """Ajoute la méthode de paiement"""
        from company_core.models.company import Company
        from billing_stripe.services.stripe_service import StripeService
        
        company = Company.objects.get(id=validated_data['company_id'])
        
        # Ajouter la méthode de paiement
        payment_method = StripeService.add_payment_method(
            company=company,
            payment_method_id=validated_data['payment_method_id']
        )
        
        # Définir comme défaut si demandé
        if validated_data['set_as_default']:
            StripeService.set_default_payment_method(
                company=company,
                payment_method_id=validated_data['payment_method_id']
            )
        
        return payment_method

class StripeSyncSerializer(serializers.Serializer):
    """Serializer pour synchroniser les données Stripe"""
    
    sync_type = serializers.ChoiceField(
        choices=[
            ('customer', 'Client'),
            ('subscription', 'Abonnement'),
            ('invoice', 'Facture'),
            ('all', 'Tout'),
        ],
        default='all'
    )
    company_id = serializers.IntegerField(required=False)
    
    def validate_company_id(self, value):
        """Valide l'ID de l'entreprise"""
        if value:
            from company_core.models.company import Company
            try:
                Company.objects.get(id=value)
                return value
            except Company.DoesNotExist:
                raise serializers.ValidationError("Entreprise non trouvée")
        return value
    
    def sync(self):
        """Effectue la synchronisation"""
        from billing_stripe.services.stripe_service import StripeService
        from company_core.models.company import Company
        
        sync_type = self.validated_data['sync_type']
        company_id = self.validated_data.get('company_id')
        
        results = {'synced': [], 'errors': []}
        
        if company_id:
            companies = [Company.objects.get(id=company_id)]
        else:
            companies = Company.objects.filter(stripe_customer_id__isnull=False)
        
        for company in companies:
            try:
                if sync_type in ['customer', 'all']:
                    StripeService.sync_customer(company)
                    results['synced'].append(f"Client {company.name}")
                
                if sync_type in ['subscription', 'all'] and hasattr(company, 'subscription'):
                    StripeService.sync_subscription(company.subscription)
                    results['synced'].append(f"Abonnement {company.name}")
                
                # Ajouter sync des factures si nécessaire
                
            except Exception as e:
                results['errors'].append(f"Erreur pour {company.name}: {str(e)}")
        
        return results
