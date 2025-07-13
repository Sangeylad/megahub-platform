# backend/company_slots/views/slots_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from company_slots.models.slots import CompanySlots
from company_slots.serializers.slots_serializers import (
    CompanySlotsSerializer, CompanySlotsUpdateSerializer, CompanySlotsStatsSerializer
)
from common.views.mixins import AnalyticsViewSetMixin

class CompanySlotsViewSet(AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des slots d'entreprise
    
    Endpoints:
    - GET /company-slots/ - Liste des slots
    - GET /company-slots/{id}/ - Détail des slots
    - PUT/PATCH /company-slots/{id}/ - Mise à jour des slots
    - POST /company-slots/{id}/refresh-counts/ - Recalcule les compteurs
    - GET /company-slots/stats/ - Statistiques générales
    """
    
    queryset = CompanySlots.objects.select_related('company').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company']
    search_fields = ['company__name']
    ordering_fields = ['brands_slots', 'users_slots', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action in ['update', 'partial_update']:
            return CompanySlotsUpdateSerializer
        elif self.action == 'stats':
            return CompanySlotsStatsSerializer
        return CompanySlotsSerializer
    
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
    def refresh_counts(self, request, pk=None):
        """
        POST /company-slots/{id}/refresh-counts/
        
        Recalcule les compteurs de brands et users
        """
        slots = self.get_object()
        
        # Recalculer les compteurs
        slots.update_brands_count()
        slots.update_users_count()
        
        # Retourner les nouvelles valeurs
        serializer = self.get_serializer(slots)
        return Response({
            'message': 'Compteurs mis à jour avec succès',
            'slots': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def usage_alerts(self, request, pk=None):
        """
        GET /company-slots/{id}/usage-alerts/
        
        Vérifie les alertes d'utilisation
        """
        slots = self.get_object()
        
        alerts = []
        
        # Vérifier les limites brands
        brands_percentage = slots.get_brands_usage_percentage()
        if brands_percentage >= 100:
            alerts.append({
                'type': 'brands_limit',
                'severity': 'error',
                'message': f'Limite de marques atteinte ({slots.current_brands_count}/{slots.brands_slots})',
                'percentage': brands_percentage
            })
        elif brands_percentage >= 80:
            alerts.append({
                'type': 'brands_warning',
                'severity': 'warning',
                'message': f'Limite de marques bientôt atteinte ({slots.current_brands_count}/{slots.brands_slots})',
                'percentage': brands_percentage
            })
        
        # Vérifier les limites users
        users_percentage = slots.get_users_usage_percentage()
        if users_percentage >= 100:
            alerts.append({
                'type': 'users_limit',
                'severity': 'error',
                'message': f"Limite d'utilisateurs atteinte ({slots.current_users_count}/{slots.users_slots})",
                'percentage': users_percentage
            })
        elif users_percentage >= 80:
            alerts.append({
                'type': 'users_warning',
                'severity': 'warning',
                'message': f"Limite d'utilisateurs bientôt atteinte ({slots.current_users_count}/{slots.users_slots})",
                'percentage': users_percentage
            })
        
        return Response({
            'company': slots.company.name,
            'alerts_count': len(alerts),
            'alerts': alerts
        })
    
    @action(detail=True, methods=['post'])
    def increase_slots(self, request, pk=None):
        """
        POST /company-slots/{id}/increase-slots/
        
        Augmente les slots (pour les upgrades)
        Body: {"brands_increment": 5, "users_increment": 10}
        """
        slots = self.get_object()
        
        brands_increment = request.data.get('brands_increment', 0)
        users_increment = request.data.get('users_increment', 0)
        
        if brands_increment < 0 or users_increment < 0:
            return Response(
                {'error': 'Les incréments doivent être positifs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if brands_increment == 0 and users_increment == 0:
            return Response(
                {'error': 'Au moins un incrément doit être spécifié'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Augmenter les slots
        old_brands_slots = slots.brands_slots
        old_users_slots = slots.users_slots
        
        slots.brands_slots += brands_increment
        slots.users_slots += users_increment
        slots.save()
        
        return Response({
            'message': 'Slots augmentés avec succès',
            'changes': {
                'brands_slots': {
                    'old': old_brands_slots,
                    'new': slots.brands_slots,
                    'increment': brands_increment
                },
                'users_slots': {
                    'old': old_users_slots,
                    'new': slots.users_slots,
                    'increment': users_increment
                }
            },
            'available_slots': {
                'brands': slots.get_available_brands_slots(),
                'users': slots.get_available_users_slots()
            }
        })
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        GET /company-slots/overview/
        
        Vue d'ensemble des slots de toutes les entreprises
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        # Statistiques globales
        total_brands_slots = sum(slots.brands_slots for slots in queryset)
        total_users_slots = sum(slots.users_slots for slots in queryset)
        total_brands_used = sum(slots.current_brands_count for slots in queryset)
        total_users_used = sum(slots.current_users_count for slots in queryset)
        
        # Entreprises proches des limites
        companies_near_limit = []
        for slots in queryset:
            if slots.get_brands_usage_percentage() >= 80 or slots.get_users_usage_percentage() >= 80:
                companies_near_limit.append({
                    'company': slots.company.name,
                    'brands_percentage': slots.get_brands_usage_percentage(),
                    'users_percentage': slots.get_users_usage_percentage(),
                })
        
        return Response({
            'total_slots': {
                'brands': total_brands_slots,
                'users': total_users_slots,
            },
            'total_used': {
                'brands': total_brands_used,
                'users': total_users_used,
            },
            'usage_percentages': {
                'brands': (total_brands_used / total_brands_slots * 100) if total_brands_slots > 0 else 0,
                'users': (total_users_used / total_users_slots * 100) if total_users_slots > 0 else 0,
            },
            'companies_near_limit': companies_near_limit,
            'companies_count': queryset.count(),
        })
    
    def perform_update(self, serializer):
        """Mise à jour avec validation"""
        slots = serializer.save()
        
        # Vérifier les alertes après mise à jour
        from billing_core.services.billing_service import BillingService
        BillingService.check_usage_limits(slots.company)
        
        return slots
