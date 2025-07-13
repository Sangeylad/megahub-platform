# backend/brands_core/views/brand_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from brands_core.models.brand import Brand
from brands_core.serializers.brand_serializers import (
    BrandSerializer, BrandListSerializer, BrandCreateSerializer,
    BrandUpdateSerializer, BrandUserAssignmentSerializer, BrandStatsSerializer
)
from common.views.mixins import (
    BrandScopedViewSetMixin, BulkActionViewSetMixin, AnalyticsViewSetMixin, 
    ExportViewSetMixin, SoftDeleteViewSetMixin
)

class BrandViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, AnalyticsViewSetMixin, 
                   ExportViewSetMixin, SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des marques
    
    Endpoints:
    - GET /brands/ - Liste des marques
    - POST /brands/ - Création de marque
    - GET /brands/{id}/ - Détail d'une marque
    - PUT/PATCH /brands/{id}/ - Mise à jour d'une marque
    - DELETE /brands/{id}/ - Suppression de marque (soft delete)
    - POST /brands/{id}/assign_users/ - Assigner des utilisateurs
    - POST /brands/{id}/remove_users/ - Retirer des utilisateurs
    - GET /brands/{id}/accessible_users/ - Utilisateurs ayant accès
    - POST /brands/{id}/set_admin/ - Définir l'admin de la marque
    - POST /brands/{id}/toggle_active/ - Activer/désactiver
    """
    
    queryset = Brand.objects.select_related('company', 'brand_admin').prefetch_related('users')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'brand_admin', 'is_active']
    search_fields = ['name', 'description', 'company__name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return BrandListSerializer
        elif self.action == 'create':
            return BrandCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BrandUpdateSerializer
        elif self.action == 'assign_users':
            return BrandUserAssignmentSerializer
        elif self.action in ['stats', 'brands_overview']:
            return BrandStatsSerializer
        return BrandSerializer
    
    # ✅ AJOUT : Méthode get_queryset pour filtrer les soft deleted
    def get_queryset(self):
        """Filtre selon les permissions utilisateur et exclut les soft deleted"""
        # Filtrer les soft deleted en premier
        queryset = super().get_queryset().filter(is_deleted=False)
        return queryset
    
    def perform_create(self, serializer):
        """Création avec vérification des limites (déjà dans le serializer)"""
        return super().perform_create(serializer)
    
    @action(detail=True, methods=['post'])
    def assign_users(self, request, pk=None):
        """
        POST /brands/{id}/assign_users/
        
        Assigne des utilisateurs à une marque
        Body: {"user_ids": [1, 2, 3]}
        """
        brand = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'brand': brand}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Utilisateurs assignés avec succès',
                'brand': brand.name,
                'assigned_users': len(serializer.validated_data['user_ids']),
                'total_users': brand.users.filter(is_active=True).count()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_users(self, request, pk=None):
        """
        POST /brands/{id}/remove_users/
        
        Retire des utilisateurs d'une marque
        Body: {"user_ids": [1, 2, 3]}
        """
        brand = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response(
                {'error': 'user_ids est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users_core.models.user import CustomUser
        users = CustomUser.objects.filter(id__in=user_ids, company=brand.company)
        
        # Retirer les utilisateurs
        removed_count = 0
        for user in users:
            if brand.users.filter(id=user.id).exists():
                brand.users.remove(user)
                removed_count += 1
        
        return Response({
            'message': 'Utilisateurs retirés avec succès',
            'brand': brand.name,
            'removed_users': removed_count,
            'total_users': brand.users.filter(is_active=True).count()
        })
    
    @action(detail=True, methods=['get'])
    def accessible_users(self, request, pk=None):
        """
        GET /brands/{id}/accessible_users/
        
        Liste des utilisateurs ayant accès à cette marque
        """
        brand = self.get_object()
        users = brand.get_accessible_users()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'is_brand_admin': user == brand.brand_admin,
                'last_login': user.last_login,
            })
        
        return Response({
            'brand': brand.name,
            'users_count': len(users_data),
            'users': users_data
        })
    
    @action(detail=True, methods=['post'])
    def set_admin(self, request, pk=None):
        """
        POST /brands/{id}/set_admin/
        
        Définit l'admin d'une marque
        Body: {"user_id": 1}
        """
        brand = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users_core.models.user import CustomUser
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Vérifier que l'utilisateur appartient à la même entreprise
            if user.company != brand.company:
                return Response(
                    {'error': 'L\'utilisateur doit appartenir à la même entreprise'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Définir comme admin
            old_admin = brand.brand_admin
            brand.brand_admin = user
            brand.save()
            
            # Ajouter l'utilisateur à la marque s'il n'y est pas déjà
            if not brand.users.filter(id=user.id).exists():
                brand.users.add(user)
            
            return Response({
                'message': 'Admin de la marque mis à jour avec succès',
                'brand': brand.name,
                'old_admin': old_admin.username if old_admin else None,
                'new_admin': user.username
            })
            
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Utilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        POST /brands/{id}/toggle_active/
        
        Active/désactive une marque
        """
        brand = self.get_object()
        brand.is_active = not brand.is_active
        brand.save()
        
        return Response({
            'message': f'Marque {"activée" if brand.is_active else "désactivée"}',
            'brand': brand.name,
            'is_active': brand.is_active
        })
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """
        GET /brands/by_company/
        
        Marques groupées par entreprise
        """
        company_id = request.query_params.get('company_id')
        if company_id:
            queryset = self.get_queryset().filter(company_id=company_id)
        else:
            queryset = self.get_queryset()
        
        # Grouper par entreprise
        brands_by_company = {}
        for brand in queryset:
            company_name = brand.company.name
            if company_name not in brands_by_company:
                brands_by_company[company_name] = []
            brands_by_company[company_name].append(
                BrandListSerializer(brand).data
            )
        
        return Response({
            'brands_by_company': brands_by_company,
            'total_brands': queryset.count(),
            'companies_count': len(brands_by_company)
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """
        GET /brands/recent_activity/
        
        Activité récente sur les marques
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Marques créées récemment
        recent_brands = self.get_queryset().filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:10]
        
        # Marques mises à jour récemment
        updated_brands = self.get_queryset().filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).exclude(
            id__in=recent_brands.values_list('id', flat=True)
        ).order_by('-updated_at')[:10]
        
        return Response({
            'recent_brands': BrandListSerializer(recent_brands, many=True).data,
            'updated_brands': BrandListSerializer(updated_brands, many=True).data,
            'total_recent': recent_brands.count(),
            'total_updated': updated_brands.count()
        })
    
    @action(detail=False, methods=['get'])
    def brands_overview(self, request):
        """
        GET /brands/brands_overview/
        
        Vue d'ensemble des marques
        """
        queryset = self.get_queryset()
        
        # Statistiques globales
        total_brands = queryset.count()
        active_brands = queryset.filter(is_active=True).count()
        brands_with_admin = queryset.filter(brand_admin__isnull=False).count()
        
        # Répartition par entreprise
        brands_by_company = queryset.values('company__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Marques les plus actives (avec le plus d'utilisateurs)
        top_brands = queryset.annotate(
            users_count=Count('users')
        ).order_by('-users_count')[:10]
        
        return Response({
            'total_brands': total_brands,
            'active_brands': active_brands,
            'brands_with_admin': brands_with_admin,
            'admin_rate': (brands_with_admin / total_brands * 100) if total_brands > 0 else 0,
            'brands_by_company': list(brands_by_company),
            'top_brands': BrandListSerializer(top_brands, many=True).data
        })