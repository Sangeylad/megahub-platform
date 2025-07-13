# backend/users_core/views/user_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout

from users_core.models.user import CustomUser
from users_core.serializers.user_serializers import (
    CustomUserSerializer, CustomUserListSerializer, CustomUserCreateSerializer,
    CustomUserUpdateSerializer, CustomUserPasswordChangeSerializer,
    CustomUserBrandAssignmentSerializer, CustomUserStatsSerializer
)
from common.views.mixins import (
    BulkActionViewSetMixin, AnalyticsViewSetMixin, ExportViewSetMixin
)

class CustomUserViewSet(BulkActionViewSetMixin, AnalyticsViewSetMixin, 
                        ExportViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs
    
    Endpoints:
    - GET /users/ - Liste des utilisateurs
    - POST /users/ - Création d'utilisateur
    - GET /users/{id}/ - Détail d'un utilisateur
    - PUT/PATCH /users/{id}/ - Mise à jour d'un utilisateur
    - DELETE /users/{id}/ - Suppression d'un utilisateur
    - POST /users/{id}/change_password/ - Changement de mot de passe
    - POST /users/{id}/assign_brands/ - Assigner des marques
    - GET /users/{id}/accessible_brands/ - Marques accessibles
    - POST /users/{id}/toggle_active/ - Activer/désactiver
    """
    
    queryset = CustomUser.objects.select_related('company').prefetch_related('brands')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'user_type', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'list':
            return CustomUserListSerializer
        elif self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomUserUpdateSerializer
        elif self.action == 'change_password':
            return CustomUserPasswordChangeSerializer
        elif self.action == 'assign_brands':
            return CustomUserBrandAssignmentSerializer
        elif self.action in ['stats', 'users_overview', 'recent_activity']:
            return CustomUserStatsSerializer
        return CustomUserSerializer
    
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
        
        # Autres utilisateurs ne voient que les utilisateurs de leur entreprise
        if user.company:
            return queryset.filter(company=user.company)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Création d'utilisateur"""
        return super().perform_create(serializer)
    
    def perform_destroy(self, instance):
        """Suppression avec vérification"""
        # Empêcher la suppression de l'admin de l'entreprise
        if instance.is_company_admin():
            raise PermissionError("Impossible de supprimer l'admin de l'entreprise")
        
        # Désactiver au lieu de supprimer
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        POST /users/{id}/change_password/
        
        Changement de mot de passe
        Body: {"current_password": "...", "new_password": "...", "new_password_confirm": "..."}
        """
        user = self.get_object()
        
        # Vérifier que l'utilisateur peut changer ce mot de passe
        if request.user != user and not request.user.is_company_admin():
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'user': user}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Mot de passe changé avec succès',
                'user': user.username
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_brands(self, request, pk=None):
        """
        POST /users/{id}/assign_brands/
        
        Assigne des marques à un utilisateur
        Body: {"brand_ids": [1, 2, 3]}
        """
        user = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'user': user}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Marques assignées avec succès',
                'user': user.username,
                'assigned_brands': len(serializer.validated_data['brand_ids']),
                'total_brands': user.brands.count()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def accessible_brands(self, request, pk=None):
        """
        GET /users/{id}/accessible_brands/
        
        Liste des marques accessibles par cet utilisateur
        """
        user = self.get_object()
        brands = user.get_accessible_brands()
        
        brands_data = []
        for brand in brands:
            brands_data.append({
                'id': brand.id,
                'name': brand.name,
                'company': brand.company.name,
                'is_admin': brand.brand_admin == user,
                'is_active': brand.is_active,
                'url': brand.url,
                'users_count': brand.users.filter(is_active=True).count()
            })
        
        return Response({
            'user': user.username,
            'brands_count': len(brands_data),
            'brands': brands_data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        POST /users/{id}/toggle_active/
        
        Active/désactive un utilisateur
        """
        user = self.get_object()
        
        # Empêcher de désactiver l'admin de l'entreprise
        if user.is_company_admin() and user.is_active:
            return Response(
                {'error': 'Impossible de désactiver l\'admin de l\'entreprise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'Utilisateur {"activé" if user.is_active else "désactivé"}',
            'user': user.username,
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'])
    def promote_to_brand_admin(self, request, pk=None):
        """
        POST /users/{id}/promote_to_brand_admin/
        
        Promeut un utilisateur en admin de marque
        Body: {"brand_id": 1}
        """
        user = self.get_object()
        brand_id = request.data.get('brand_id')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from brands_core.models.brand import Brand
        try:
            brand = Brand.objects.get(id=brand_id, company=user.company)
            
            # Vérifier que l'utilisateur a accès à cette marque
            if not user.can_access_brand(brand):
                return Response(
                    {'error': 'L\'utilisateur n\'a pas accès à cette marque'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Définir comme admin
            old_admin = brand.brand_admin
            brand.brand_admin = user
            brand.save()
            
            return Response({
                'message': 'Utilisateur promu admin de la marque',
                'user': user.username,
                'brand': brand.name,
                'old_admin': old_admin.username if old_admin else None
            })
            
        except Brand.DoesNotExist:
            return Response(
                {'error': 'Marque non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """
        GET /users/by_company/
        
        Utilisateurs groupés par entreprise
        """
        company_id = request.query_params.get('company_id')
        if company_id:
            queryset = self.get_queryset().filter(company_id=company_id)
        else:
            queryset = self.get_queryset()
        
        # Grouper par entreprise
        users_by_company = {}
        for user in queryset:
            company_name = user.company.name if user.company else 'Sans entreprise'
            if company_name not in users_by_company:
                users_by_company[company_name] = []
            users_by_company[company_name].append(
                CustomUserListSerializer(user).data
            )
        
        return Response({
            'users_by_company': users_by_company,
            'total_users': queryset.count(),
            'companies_count': len(users_by_company)
        })
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        GET /users/by_type/
        
        Utilisateurs groupés par type
        """
        queryset = self.get_queryset()
        
        # Grouper par type d'utilisateur
        users_by_type = {}
        for user in queryset:
            user_type = user.get_user_type_display()
            if user_type not in users_by_type:
                users_by_type[user_type] = []
            users_by_type[user_type].append(
                CustomUserListSerializer(user).data
            )
        
        return Response({
            'users_by_type': users_by_type,
            'total_users': queryset.count(),
            'types_count': len(users_by_type)
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """
        GET /users/recent_activity/
        
        Activité récente des utilisateurs
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Utilisateurs créés récemment
        recent_users = self.get_queryset().filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).order_by('-date_joined')[:10]
        
        # Utilisateurs connectés récemment
        active_users = self.get_queryset().filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        ).order_by('-last_login')[:10]
        
        return Response({
            'recent_users': CustomUserListSerializer(recent_users, many=True).data,
            'active_users': CustomUserListSerializer(active_users, many=True).data,
            'total_recent': recent_users.count(),
            'total_active': active_users.count()
        })
    
    @action(detail=False, methods=['get'])
    def users_overview(self, request):
        """
        GET /users/users_overview/
        
        Vue d'ensemble des utilisateurs
        """
        queryset = self.get_queryset()
        
        # Statistiques globales
        total_users = queryset.count()
        active_users = queryset.filter(is_active=True).count()
        
        # Répartition par type
        users_by_type = queryset.values('user_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Répartition par entreprise
        users_by_company = queryset.values('company__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Utilisateurs les plus actifs (avec le plus de marques)
        top_users = queryset.annotate(
            brands_count=Count('brands')
        ).order_by('-brands_count')[:10]
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'activation_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'users_by_type': list(users_by_type),
            'users_by_company': list(users_by_company),
            'top_users': CustomUserListSerializer(top_users, many=True).data
        })