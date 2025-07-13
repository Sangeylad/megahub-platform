# backend/billing_core/views/billing_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.utils import timezone

from billing_core.models.billing import Plan, Subscription, Invoice, InvoiceItem, UsageAlert
from billing_core.serializers.billing_serializers import (
    PlanSerializer, PlanListSerializer, SubscriptionSerializer, SubscriptionListSerializer,
    InvoiceSerializer, InvoiceListSerializer, InvoiceItemSerializer, UsageAlertSerializer,
    BillingSummarySerializer, SubscriptionCreateSerializer, SubscriptionUpdateSerializer
)
from billing_core.services.billing_service import BillingService
from common.views.mixins import AnalyticsViewSetMixin, ExportViewSetMixin

class PlanViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des plans
    
    Endpoints:
    - GET /plans/ - Liste des plans
    - GET /plans/{id}/ - Détail d'un plan
    - GET /plans/calculate-price/ - Calcul de prix
    """
    
    queryset = Plan.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filterset_fields = ['plan_type', 'billing_interval', 'is_featured']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['sort_order', 'price', 'created_at']
    ordering = ['sort_order', 'price']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return PlanListSerializer
        return PlanSerializer
    
    @action(detail=False, methods=['get'])
    def calculate_price(self, request):
        """
        GET /plans/calculate-price/
        
        Calcule le prix pour une configuration donnée
        Query params: plan_id, brands_slots, users_slots
        """
        plan_id = request.query_params.get('plan_id')
        brands_slots = request.query_params.get('brands_slots', 0)
        users_slots = request.query_params.get('users_slots', 0)
        
        if not plan_id:
            return Response(
                {'error': 'plan_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
            brands_slots = int(brands_slots)
            users_slots = int(users_slots)
            
            total_price = plan.get_total_price_for_slots(brands_slots, users_slots)
            
            # Détail du calcul
            additional_brands = max(0, brands_slots - plan.included_brands_slots)
            additional_users = max(0, users_slots - plan.included_users_slots)
            
            return Response({
                'plan': plan.display_name,
                'base_price': plan.price,
                'additional_costs': {
                    'brands': additional_brands * plan.additional_brand_price,
                    'users': additional_users * plan.additional_user_price,
                },
                'total_price': total_price,
                'breakdown': {
                    'included_brands': plan.included_brands_slots,
                    'included_users': plan.included_users_slots,
                    'additional_brands': additional_brands,
                    'additional_users': additional_users,
                    'additional_brand_price': plan.additional_brand_price,
                    'additional_user_price': plan.additional_user_price,
                }
            })
            
        except Plan.DoesNotExist:
            return Response(
                {'error': 'Plan non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'brands_slots et users_slots doivent être des nombres'},
                status=status.HTTP_400_BAD_REQUEST
            )

class SubscriptionViewSet(AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des abonnements
    
    Endpoints:
    - GET /subscriptions/ - Liste des abonnements
    - POST /subscriptions/ - Création d'abonnement
    - GET /subscriptions/{id}/ - Détail d'un abonnement
    - PUT/PATCH /subscriptions/{id}/ - Mise à jour d'abonnement
    - DELETE /subscriptions/{id}/ - Annulation d'abonnement
    - POST /subscriptions/{id}/cancel/ - Annulation d'abonnement
    - POST /subscriptions/{id}/upgrade/ - Upgrade d'abonnement
    """
    
    queryset = Subscription.objects.select_related('company', 'plan').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'plan', 'status']
    search_fields = ['company__name', 'plan__display_name']
    ordering_fields = ['started_at', 'current_period_end', 'amount']
    ordering = ['-started_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return SubscriptionListSerializer
        elif self.action == 'create':
            return SubscriptionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SubscriptionUpdateSerializer
        return SubscriptionSerializer
    
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
    def cancel(self, request, pk=None):
        """
        POST /subscriptions/{id}/cancel/
        
        Annule un abonnement
        Body: {"cancel_at_period_end": true}
        """
        subscription = self.get_object()
        cancel_at_period_end = request.data.get('cancel_at_period_end', True)
        
        if subscription.status == 'canceled':
            return Response(
                {'error': 'Abonnement déjà annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription = BillingService.cancel_subscription(
            subscription,
            cancel_at_period_end=cancel_at_period_end
        )
        
        return Response({
            'message': 'Abonnement annulé avec succès',
            'subscription_id': subscription.id,
            'canceled_at': subscription.canceled_at,
            'cancel_at_period_end': cancel_at_period_end
        })
    
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """
        POST /subscriptions/{id}/upgrade/
        
        Upgrade un abonnement
        Body: {"new_plan_id": 1}
        """
        subscription = self.get_object()
        new_plan_id = request.data.get('new_plan_id')
        
        if not new_plan_id:
            return Response(
                {'error': 'new_plan_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_plan = Plan.objects.get(id=new_plan_id, is_active=True)
            
            old_plan = subscription.plan
            subscription = BillingService.upgrade_subscription(subscription, new_plan)
            
            return Response({
                'message': 'Abonnement mis à jour avec succès',
                'subscription_id': subscription.id,
                'old_plan': old_plan.display_name,
                'new_plan': new_plan.display_name,
                'new_amount': subscription.amount
            })
            
        except Plan.DoesNotExist:
            return Response(
                {'error': 'Plan non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def billing_summary(self, request, pk=None):
        """
        GET /subscriptions/{id}/billing-summary/
        
        Résumé de facturation pour un abonnement
        """
        subscription = self.get_object()
        summary = BillingService.get_billing_summary(subscription.company)
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        GET /subscriptions/overview/
        
        Vue d'ensemble des abonnements
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        # Statistiques globales
        total_subscriptions = queryset.count()
        active_subscriptions = queryset.filter(status__in=['active', 'trialing']).count()
        trial_subscriptions = queryset.filter(status='trialing').count()
        
        # Revenus
        monthly_revenue = queryset.filter(
            status='active',
            plan__billing_interval='monthly'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        yearly_revenue = queryset.filter(
            status='active',
            plan__billing_interval='yearly'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Répartition par plan
        subscriptions_by_plan = queryset.values('plan__display_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Répartition par statut
        subscriptions_by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
            'activation_rate': (active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0,
            'revenue': {
                'monthly': monthly_revenue,
                'yearly': yearly_revenue,
                'total_monthly_recurring': monthly_revenue + (yearly_revenue / 12),
            },
            'subscriptions_by_plan': list(subscriptions_by_plan),
            'subscriptions_by_status': list(subscriptions_by_status)
        })

class InvoiceViewSet(AnalyticsViewSetMixin, ExportViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des factures
    
    Endpoints:
    - GET /invoices/ - Liste des factures
    - GET /invoices/{id}/ - Détail d'une facture
    - POST /invoices/{id}/mark-paid/ - Marquer comme payée
    - GET /invoices/overdue/ - Factures en retard
    """
    
    queryset = Invoice.objects.select_related('company', 'subscription').prefetch_related('items')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'subscription', 'status']
    search_fields = ['invoice_number', 'company__name']
    ordering_fields = ['invoice_date', 'due_date', 'total']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
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
    def mark_paid(self, request, pk=None):
        """
        POST /invoices/{id}/mark-paid/
        
        Marque une facture comme payée
        """
        invoice = self.get_object()
        
        if invoice.status == 'paid':
            return Response(
                {'error': 'Facture déjà payée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        
        return Response({
            'message': 'Facture marquée comme payée',
            'invoice_number': invoice.invoice_number,
            'paid_at': invoice.paid_at
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        GET /invoices/overdue/
        
        Factures en retard
        """
        overdue_invoices = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['open', 'past_due']
        ).order_by('due_date')
        
        return Response({
            'overdue_count': overdue_invoices.count(),
            'overdue_invoices': InvoiceListSerializer(overdue_invoices, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def revenue_stats(self, request):
        """
        GET /invoices/revenue-stats/
        
        Statistiques de revenus
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        # Revenus par statut
        revenue_by_status = queryset.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('total')
        ).order_by('-total_amount')
        
        # Revenus par mois
        from django.db.models import DateTrunc
        revenue_by_month = queryset.filter(
            status='paid'
        ).annotate(
            month=DateTrunc('month', 'paid_at')
        ).values('month').annotate(
            count=Count('id'),
            total_amount=Sum('total')
        ).order_by('-month')[:12]
        
        return Response({
            'revenue_by_status': list(revenue_by_status),
            'revenue_by_month': list(revenue_by_month)
        })

class UsageAlertViewSet(AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des alertes d'utilisation
    
    Endpoints:
    - GET /usage-alerts/ - Liste des alertes
    - GET /usage-alerts/{id}/ - Détail d'une alerte
    - POST /usage-alerts/{id}/resolve/ - Résoudre une alerte
    - POST /usage-alerts/{id}/dismiss/ - Ignorer une alerte
    """
    
    queryset = UsageAlert.objects.select_related('company').all()
    serializer_class = UsageAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'alert_type', 'status']
    search_fields = ['company__name', 'message']
    ordering_fields = ['triggered_at', 'resolved_at']
    ordering = ['-triggered_at']
    
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
    def resolve(self, request, pk=None):
        """
        POST /usage-alerts/{id}/resolve/
        
        Résout une alerte
        """
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response(
                {'error': 'Alerte déjà résolue'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.resolve()
        
        return Response({
            'message': 'Alerte résolue avec succès',
            'alert_id': alert.id,
            'resolved_at': alert.resolved_at
        })
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """
        POST /usage-alerts/{id}/dismiss/
        
        Ignore une alerte
        """
        alert = self.get_object()
        
        if alert.status == 'dismissed':
            return Response(
                {'error': 'Alerte déjà ignorée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.dismiss()
        
        return Response({
            'message': 'Alerte ignorée avec succès',
            'alert_id': alert.id,
            'resolved_at': alert.resolved_at
        })
    
    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """
        GET /usage-alerts/active-alerts/
        
        Alertes actives
        """
        active_alerts = self.get_queryset().filter(status='active')
        
        # Grouper par type
        alerts_by_type = {}
        for alert in active_alerts:
            alert_type = alert.get_alert_type_display()
            if alert_type not in alerts_by_type:
                alerts_by_type[alert_type] = []
            alerts_by_type[alert_type].append(
                UsageAlertSerializer(alert).data
            )
        
        return Response({
            'active_alerts_count': active_alerts.count(),
            'alerts_by_type': alerts_by_type
        })
