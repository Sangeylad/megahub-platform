# backend/company_features/views/features_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from company_features.models.features import Feature, CompanyFeature
from company_features.serializers.features_serializers import (
    FeatureSerializer, CompanyFeatureSerializer, CompanyFeatureListSerializer,
    CompanyFeatureCreateSerializer, CompanyFeatureUpdateSerializer,
    FeatureUsageSerializer, CompanyFeaturesOverviewSerializer
)
from common.views.mixins import BulkActionViewSetMixin, AnalyticsViewSetMixin

class FeatureViewSet(AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des features
    
    Endpoints:
    - GET /features/ - Liste des features
    - POST /features/ - Création de feature (admin seulement)
    - GET /features/{id}/ - Détail d'une feature
    - PUT/PATCH /features/{id}/ - Mise à jour d'une feature
    - DELETE /features/{id}/ - Suppression d'une feature
    """
    
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['feature_type', 'is_active', 'is_premium']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['sort_order', 'display_name', 'created_at']
    ordering = ['sort_order', 'display_name']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        # Tous les utilisateurs peuvent voir les features actives
        return super().get_queryset().filter(is_active=True)
    
    def perform_create(self, serializer):
        """Création (admin seulement)"""
        if not self.request.user.is_superuser:
            raise PermissionError("Seuls les administrateurs peuvent créer des features")
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Mise à jour (admin seulement)"""
        if not self.request.user.is_superuser:
            raise PermissionError("Seuls les administrateurs peuvent modifier des features")
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Suppression (admin seulement)"""
        if not self.request.user.is_superuser:
            raise PermissionError("Seuls les administrateurs peuvent supprimer des features")
        return super().perform_destroy(instance)

class CompanyFeatureViewSet(BulkActionViewSetMixin, AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des features d'entreprise
    
    Endpoints:
    - GET /company-features/ - Liste des features d'entreprise
    - POST /company-features/ - Abonnement à une feature
    - GET /company-features/{id}/ - Détail d'une feature d'entreprise
    - PUT/PATCH /company-features/{id}/ - Mise à jour d'une feature d'entreprise
    - DELETE /company-features/{id}/ - Désabonnement d'une feature
    - POST /company-features/{id}/increment-usage/ - Incrémente l'utilisation
    - POST /company-features/{id}/reset-usage/ - Remet à zéro l'utilisation
    """
    
    queryset = CompanyFeature.objects.select_related('company', 'feature').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'feature', 'is_enabled']
    search_fields = ['company__name', 'feature__display_name']
    ordering_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return CompanyFeatureListSerializer
        elif self.action == 'create':
            return CompanyFeatureCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CompanyFeatureUpdateSerializer
        elif self.action == 'usage_stats':
            return FeatureUsageSerializer
        return CompanyFeatureSerializer
    
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
    def increment_usage(self, request, pk=None):
        """
        POST /company-features/{id}/increment-usage/
        
        Incrémente l'utilisation d'une feature
        Body: {"amount": 1}
        """
        company_feature = self.get_object()
        amount = request.data.get('amount', 1)
        
        if amount <= 0:
            return Response(
                {'error': 'Le montant doit être positif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier la limite
        if company_feature.usage_limit and (company_feature.current_usage + amount) > company_feature.usage_limit:
            return Response(
                {'error': f'Limite d\'utilisation atteinte ({company_feature.usage_limit})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company_feature.increment_usage(amount)
        
        return Response({
            'message': f'Utilisation incrémentée de {amount}',
            'current_usage': company_feature.current_usage,
            'usage_limit': company_feature.usage_limit,
            'usage_percentage': company_feature.get_usage_percentage(),
            'limit_reached': company_feature.is_usage_limit_reached()
        })
    
    @action(detail=True, methods=['post'])
    def reset_usage(self, request, pk=None):
        """
        POST /company-features/{id}/reset-usage/
        
        Remet à zéro l'utilisation d'une feature
        """
        company_feature = self.get_object()
        old_usage = company_feature.current_usage
        
        company_feature.reset_usage()
        
        return Response({
            'message': 'Utilisation remise à zéro',
            'old_usage': old_usage,
            'current_usage': company_feature.current_usage
        })
    
    @action(detail=True, methods=['post'])
    def toggle_enabled(self, request, pk=None):
        """
        POST /company-features/{id}/toggle-enabled/
        
        Active/désactive une feature pour une entreprise
        """
        company_feature = self.get_object()
        company_feature.is_enabled = not company_feature.is_enabled
        company_feature.save()
        
        return Response({
            'message': f'Feature {"activée" if company_feature.is_enabled else "désactivée"}',
            'is_enabled': company_feature.is_enabled,
            'is_active': company_feature.is_active()
        })
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """
        GET /company-features/by-company/
        
        Features groupées par entreprise
        """
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response(
                {'error': 'company_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(company_id=company_id)
        
        # Grouper par type de feature
        features_by_type = {}
        for company_feature in queryset:
            feature_type = company_feature.feature.feature_type
            if feature_type not in features_by_type:
                features_by_type[feature_type] = []
            features_by_type[feature_type].append(
                CompanyFeatureListSerializer(company_feature).data
            )
        
        return Response({
            'company_id': company_id,
            'features_by_type': features_by_type,
            'total_features': queryset.count(),
            'active_features': queryset.filter(is_enabled=True).count()
        })
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """
        GET /company-features/usage-stats/
        
        Statistiques d'utilisation des features
        """
        queryset = self.get_queryset()
        
        # Stats globales
        total_features = queryset.count()
        active_features = queryset.filter(is_enabled=True).count()
        over_limit_features = sum(1 for cf in queryset if cf.is_usage_limit_reached())
        
        # Stats par type
        stats_by_type = {}
        for company_feature in queryset:
            feature_type = company_feature.feature.feature_type
            if feature_type not in stats_by_type:
                stats_by_type[feature_type] = {
                    'total': 0,
                    'active': 0,
                    'over_limit': 0,
                    'total_usage': 0
                }
            
            stats_by_type[feature_type]['total'] += 1
            if company_feature.is_enabled:
                stats_by_type[feature_type]['active'] += 1
            if company_feature.is_usage_limit_reached():
                stats_by_type[feature_type]['over_limit'] += 1
            stats_by_type[feature_type]['total_usage'] += company_feature.current_usage
        
        return Response({
            'global_stats': {
                'total_features': total_features,
                'active_features': active_features,
                'over_limit_features': over_limit_features,
                'activation_rate': (active_features / total_features * 100) if total_features > 0 else 0,
            },
            'stats_by_type': stats_by_type
        })
    
    @action(detail=False, methods=['get'])
    def companies_overview(self, request):
        """
        GET /company-features/companies-overview/
        
        Vue d'ensemble des features par entreprise
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Grouper par entreprise
        from company_core.models.company import Company
        companies = Company.objects.prefetch_related('company_features__feature')
        
        companies_data = []
        for company in companies:
            overview = CompanyFeaturesOverviewSerializer(company).data
            companies_data.append(overview)
        
        return Response({
            'companies_count': len(companies_data),
            'companies': companies_data
        })
