# backend/billing_core/serializers/billing_serializers.py
from rest_framework import serializers
from decimal import Decimal
from billing_core.models.billing import Plan, Subscription, Invoice, InvoiceItem, UsageAlert

class PlanSerializer(serializers.ModelSerializer):
    """Serializer pour Plan"""
    
    # Champs calculés
    total_price_example = serializers.SerializerMethodField()
    features_summary = serializers.SerializerMethodField()
    subscriptions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'display_name', 'description', 'plan_type',
            'price', 'billing_interval', 'included_brands_slots', 'included_users_slots',
            'additional_brand_price', 'additional_user_price',
            'is_active', 'is_featured', 'stripe_price_id', 'sort_order',
            'total_price_example', 'features_summary', 'subscriptions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_price_example(self, obj):
        """Exemple de prix total avec usage standard"""
        # Exemple avec 10 brands et 20 users
        return obj.get_total_price_for_slots(10, 20)
    
    def get_features_summary(self, obj):
        """Résumé des features du plan"""
        return obj.get_features_summary()
    
    def get_subscriptions_count(self, obj):
        """Nombre d'abonnements actifs sur ce plan"""
        return obj.subscriptions.filter(status__in=['active', 'trialing']).count()
    
    def validate_price(self, value):
        """Validation du prix"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Le prix ne peut pas être négatif")
        return value
    
    def validate_additional_brand_price(self, value):
        """Validation du prix par brand supplémentaire"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Le prix par brand supplémentaire ne peut pas être négatif")
        return value
    
    def validate_additional_user_price(self, value):
        """Validation du prix par user supplémentaire"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Le prix par user supplémentaire ne peut pas être négatif")
        return value

class PlanListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes de plans"""
    
    subscriptions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'display_name', 'plan_type', 'price', 'billing_interval',
            'included_brands_slots', 'included_users_slots', 'is_active', 'is_featured',
            'subscriptions_count', 'sort_order'
        ]
    
    def get_subscriptions_count(self, obj):
        return obj.subscriptions.filter(status__in=['active', 'trialing']).count()

class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour Subscription"""
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_billing_email = serializers.CharField(source='company.billing_email', read_only=True)
    
    # Informations du plan
    plan_name = serializers.CharField(source='plan.display_name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    
    # Champs calculés
    is_active_status = serializers.SerializerMethodField()
    is_trial_status = serializers.SerializerMethodField()
    days_until_renewal = serializers.SerializerMethodField()
    usage_summary = serializers.SerializerMethodField()
    
    # Informations Stripe
    stripe_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'company', 'company_name', 'company_billing_email',
            'plan', 'plan_name', 'plan_type', 'status',
            'started_at', 'current_period_start', 'current_period_end',
            'trial_end', 'canceled_at', 'amount', 'stripe_subscription_id',
            'is_active_status', 'is_trial_status', 'days_until_renewal',
            'usage_summary', 'stripe_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_active_status(self, obj):
        """Statut d'activation de l'abonnement"""
        return obj.is_active()
    
    def get_is_trial_status(self, obj):
        """Statut de période d'essai"""
        return obj.is_trial()
    
    def get_days_until_renewal(self, obj):
        """Jours jusqu'au renouvellement"""
        return obj.days_until_renewal()
    
    def get_usage_summary(self, obj):
        """Résumé de l'utilisation"""
        return obj.get_usage_summary()
    
    def get_stripe_info(self, obj):
        """Informations Stripe (si disponibles)"""
        try:
            stripe_subscription = obj.stripe_subscription
            return {
                'stripe_subscription_id': stripe_subscription.stripe_subscription_id,
                'stripe_status': stripe_subscription.stripe_status,
                'last_sync_at': stripe_subscription.last_sync_at,
            }
        except:
            return None

class SubscriptionListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes d'abonnements"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    plan_name = serializers.CharField(source='plan.display_name', read_only=True)
    days_until_renewal = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'company_name', 'plan_name', 'status', 'amount',
            'current_period_end', 'days_until_renewal', 'created_at'
        ]
    
    def get_days_until_renewal(self, obj):
        return obj.days_until_renewal()

class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer pour Invoice"""
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_billing_email = serializers.CharField(source='company.billing_email', read_only=True)
    
    # Informations du plan
    plan_name = serializers.CharField(source='subscription.plan.display_name', read_only=True)
    
    # Champs calculés
    is_overdue_status = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    
    # Ligne de facture
    items_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'company', 'company_name', 'company_billing_email',
            'subscription', 'plan_name', 'invoice_number', 'status',
            'subtotal', 'tax_amount', 'total', 'invoice_date', 'due_date', 'paid_at',
            'period_start', 'period_end', 'stripe_invoice_id',
            'is_overdue_status', 'days_overdue', 'items_list',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['invoice_number', 'created_at', 'updated_at']
    
    def get_is_overdue_status(self, obj):
        """Statut de retard de paiement"""
        return obj.is_overdue()
    
    def get_days_overdue(self, obj):
        """Nombre de jours de retard"""
        return obj.days_overdue()
    
    def get_items_list(self, obj):
        """Liste des items de facture"""
        return InvoiceItemSerializer(obj.items.all(), many=True).data

class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes de factures"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    is_overdue_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'company_name', 'invoice_number', 'status', 'total',
            'invoice_date', 'due_date', 'paid_at', 'is_overdue_status'
        ]
    
    def get_is_overdue_status(self, obj):
        return obj.is_overdue()

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer pour InvoiceItem"""
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'description', 'quantity', 'unit_price',
            'total_price', 'item_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_price', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        return value
    
    def validate_unit_price(self, value):
        """Validation du prix unitaire"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Le prix unitaire ne peut pas être négatif")
        return value

class UsageAlertSerializer(serializers.ModelSerializer):
    """Serializer pour UsageAlert"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = UsageAlert
        fields = [
            'id', 'company', 'company_name', 'alert_type', 'status',
            'message', 'triggered_at', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['triggered_at', 'resolved_at', 'created_at', 'updated_at']

class BillingSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé de facturation d'une entreprise"""
    
    company_name = serializers.CharField()
    current_plan = serializers.CharField()
    subscription_status = serializers.CharField()
    current_period_end = serializers.DateTimeField()
    monthly_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    slots_usage = serializers.DictField()
    next_invoice_date = serializers.DateTimeField()
    days_until_renewal = serializers.IntegerField()
    recent_invoices = serializers.ListField()
    active_alerts = serializers.ListField()
    
    def to_representation(self, company):
        """Génère le résumé pour une entreprise"""
        from billing_core.services.billing_service import BillingService
        
        try:
            summary = BillingService.get_billing_summary(company)
            
            # Ajouter les factures récentes
            recent_invoices = company.invoices.filter(
                status__in=['open', 'paid']
            ).order_by('-invoice_date')[:5]
            
            summary['recent_invoices'] = InvoiceListSerializer(recent_invoices, many=True).data
            
            # Ajouter les alertes actives
            active_alerts = company.usage_alerts.filter(status='active')
            summary['active_alerts'] = UsageAlertSerializer(active_alerts, many=True).data
            
            return summary
        except Exception as e:
            return {
                'company_name': company.name,
                'error': str(e),
                'current_plan': None,
                'subscription_status': 'Erreur',
            }

class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer pour créer un abonnement"""
    
    company_id = serializers.IntegerField()
    plan_id = serializers.IntegerField()
    trial_days = serializers.IntegerField(required=False, min_value=0, max_value=90)
    payment_method_id = serializers.CharField(required=False)
    
    def validate_company_id(self, value):
        """Valide l'ID de l'entreprise"""
        from company_core.models.company import Company
        
        try:
            company = Company.objects.get(id=value)
            # Vérifier qu'il n'y a pas déjà un abonnement actif
            if hasattr(company, 'subscription') and company.subscription.is_active():
                raise serializers.ValidationError("Cette entreprise a déjà un abonnement actif")
            return value
        except Company.DoesNotExist:
            raise serializers.ValidationError("Entreprise non trouvée")
    
    def validate_plan_id(self, value):
        """Valide l'ID du plan"""
        try:
            plan = Plan.objects.get(id=value, is_active=True)
            return value
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan non trouvé ou inactif")
    
    def create(self, validated_data):
        """Crée l'abonnement"""
        from company_core.models.company import Company
        from billing_core.services.billing_service import BillingService
        
        company = Company.objects.get(id=validated_data['company_id'])
        plan = Plan.objects.get(id=validated_data['plan_id'])
        
        subscription = BillingService.create_subscription(
            company=company,
            plan=plan,
            trial_days=validated_data.get('trial_days')
        )
        
        return subscription

class SubscriptionUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour un abonnement"""
    
    new_plan_id = serializers.IntegerField(required=False)
    cancel_at_period_end = serializers.BooleanField(required=False)
    
    def validate_new_plan_id(self, value):
        """Valide le nouveau plan"""
        if value:
            try:
                plan = Plan.objects.get(id=value, is_active=True)
                return value
            except Plan.DoesNotExist:
                raise serializers.ValidationError("Plan non trouvé ou inactif")
        return value
    
    def update(self, instance, validated_data):
        """Met à jour l'abonnement"""
        from billing_core.services.billing_service import BillingService
        
        if 'new_plan_id' in validated_data:
            new_plan = Plan.objects.get(id=validated_data['new_plan_id'])
            instance = BillingService.upgrade_subscription(instance, new_plan)
        
        if 'cancel_at_period_end' in validated_data:
            if validated_data['cancel_at_period_end']:
                instance = BillingService.cancel_subscription(instance, cancel_at_period_end=True)
        
        return instance
