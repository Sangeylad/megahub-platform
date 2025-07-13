# backend/company_core/views/company_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Prefetch
from django.utils import timezone

from company_core.models.company import Company
from company_core.serializers.company_serializers import (
    CompanySerializer, CompanyListSerializer, CompanyCreateSerializer, CompanyUpdateSerializer
)
from common.views.mixins import (
    BulkActionViewSetMixin, AnalyticsViewSetMixin, ExportViewSetMixin
)
# ✅ CORRECTION : Import ajouté
from company_slots.models.slots import CompanySlots

class CompanyViewSet(BulkActionViewSetMixin, AnalyticsViewSetMixin, ExportViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des entreprises
    
    Endpoints:
    - GET /companies/ - Liste des entreprises
    - POST /companies/ - Création d'entreprise (superuser seulement)
    - GET /companies/{id}/ - Détail d'une entreprise
    - PUT/PATCH /companies/{id}/ - Mise à jour d'une entreprise
    - DELETE /companies/{id}/ - Suppression d'une entreprise
    - POST /companies/{id}/check_limits/ - Vérifier les limites
    - GET /companies/{id}/usage_stats/ - Statistiques d'utilisation
    - POST /companies/{id}/upgrade_slots/ - Augmenter les slots
    """
    
    queryset = Company.objects.select_related('admin').prefetch_related(
        'brands', 'members', 'slots'
    )
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'admin']
    search_fields = ['name', 'billing_email', 'admin__username']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return CompanyListSerializer
        elif self.action == 'create':
            return CompanyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CompanyUpdateSerializer
        return CompanySerializer
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin ne voit que son entreprise
        if user.is_company_admin():
            return queryset.filter(id=user.company_id)
        
        # Autres utilisateurs ne voient que leur entreprise
        if user.company:
            return queryset.filter(id=user.company_id)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Création (superuser seulement)"""
        if not self.request.user.is_superuser:
            # ✅ CORRECTION : Utiliser l'exception DRF
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les administrateurs peuvent créer des entreprises")
        return super().perform_create(serializer)
    
    def perform_destroy(self, instance):
        """Suppression logique"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def check_limits(self, request, pk=None):
        """
        POST /companies/{id}/check_limits/
        
        Vérifie les limites d'utilisation et génère des alertes
        """
        company = self.get_object()
        
        # Simuler la vérification des limites (à adapter selon votre logique métier)
        alerts = []
        
        try:
            slots = company.slots
            
            # Vérifier les limites brands
            if slots.current_brands_count >= slots.brands_slots:
                alerts.append({
                    'type': 'brands_limit',
                    'message': f'Limite de marques atteinte ({slots.current_brands_count}/{slots.brands_slots})',
                    'triggered_at': timezone.now()
                })
            
            # Vérifier les limites users
            if slots.current_users_count >= slots.users_slots:
                alerts.append({
                    'type': 'users_limit',
                    'message': f'Limite d\'utilisateurs atteinte ({slots.current_users_count}/{slots.users_slots})',
                    'triggered_at': timezone.now()
                })
        
        except Exception:
            # Si pas de slots, pas d'alertes
            pass
        
        return Response({
            'company': company.name,
            'alerts_generated': len(alerts),
            'alerts': alerts
        })
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """
        GET /companies/{id}/usage_stats/
        
        Statistiques d'utilisation détaillées
        """
        company = self.get_object()
        
        try:
            slots = company.slots
            brands = company.brands.filter(is_deleted=False)
            users = company.members.filter(is_active=True)
            
            # Calculs d'utilisation
            brands_by_month = brands.extra(
                select={'month': "DATE_TRUNC('month', created_at)"}
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            users_by_type = users.values('user_type').annotate(count=Count('id'))
            
            stats = {
                'slots': {
                    'brands': {
                        'total': slots.brands_slots,
                        'used': slots.current_brands_count,
                        'percentage': slots.get_brands_usage_percentage(),
                        'available': slots.get_available_brands_slots(),
                    },
                    'users': {
                        'total': slots.users_slots,
                        'used': slots.current_users_count,
                        'percentage': slots.get_users_usage_percentage(),
                        'available': slots.get_available_users_slots(),
                    }
                },
                'growth': {
                    'brands_by_month': list(brands_by_month),
                    'users_by_type': list(users_by_type),
                },
                'activity': {
                    'total_brands': brands.count(),
                    'active_brands': brands.filter(is_active=True).count(),
                    'total_users': users.count(),
                    'recent_logins': users.filter(
                        last_login__gte=timezone.now() - timezone.timedelta(days=30)
                    ).count(),
                }
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def upgrade_slots(self, request, pk=None):
        """
        POST /companies/{id}/upgrade_slots/
        
        Augmente les slots d'une entreprise
        Body: {"brands_slots": 10, "users_slots": 20}
        """
        company = self.get_object()
        
        brands_slots = request.data.get('brands_slots')
        users_slots = request.data.get('users_slots')
        
        if not brands_slots and not users_slots:
            return Response(
                {'error': 'Au moins brands_slots ou users_slots est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # ✅ CORRECTION : Gérer le cas où slots n'existe pas
            slots, created = CompanySlots.objects.get_or_create(
                company=company,
                defaults={
                    'brands_slots': 5,
                    'users_slots': 10,
                    'current_brands_count': 0,
                    'current_users_count': 1
                }
            )
            
            if brands_slots:
                brands_slots = int(brands_slots)
                if brands_slots < slots.current_brands_count:
                    return Response(
                        {'error': f'Impossible de réduire à {brands_slots} slots, {slots.current_brands_count} brands utilisées'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                slots.brands_slots = brands_slots
            
            if users_slots:
                users_slots = int(users_slots)
                if users_slots < slots.current_users_count:
                    return Response(
                        {'error': f'Impossible de réduire à {users_slots} slots, {slots.current_users_count} users actifs'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                slots.users_slots = users_slots
            
            slots.save()
            
            return Response({
                'message': 'Slots mis à jour avec succès',
                'brands_slots': slots.brands_slots,
                'users_slots': slots.users_slots,
                'brands_available': slots.brands_slots - slots.current_brands_count,
                'users_available': slots.users_slots - slots.current_users_count,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )