# backend/users_roles/views/roles_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from users_roles.models.roles import Role, UserRole, Permission, RolePermission
from users_roles.serializers.roles_serializers import (
    RoleSerializer, PermissionSerializer, RolePermissionSerializer,
    UserRoleSerializer, UserRoleCreateSerializer, UserRoleUpdateSerializer,
    RolePermissionAssignmentSerializer, UserPermissionsOverviewSerializer
)
from common.views.mixins import BulkActionViewSetMixin, AnalyticsViewSetMixin

class RoleViewSet(BulkActionViewSetMixin, AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des rôles
    
    Endpoints:
    - GET /roles/ - Liste des rôles
    - POST /roles/ - Création de rôle
    - GET /roles/{id}/ - Détail d'un rôle
    - PUT/PATCH /roles/{id}/ - Mise à jour d'un rôle
    - DELETE /roles/{id}/ - Suppression d'un rôle
    - POST /roles/{id}/assign-permissions/ - Assigner des permissions
    - GET /roles/{id}/users/ - Utilisateurs avec ce rôle
    """
    
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role_type', 'is_active', 'is_system']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['name', 'display_name', 'role_type', 'created_at']
    ordering = ['role_type', 'name']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        # Seuls les admins peuvent gérer les rôles
        if self.request.user.is_superuser or self.request.user.is_company_admin():
            return super().get_queryset()
        
        # Autres utilisateurs voient seulement les rôles actifs
        return super().get_queryset().filter(is_active=True)
    
    def perform_create(self, serializer):
        """Création (admin seulement)"""
        if not (self.request.user.is_superuser or self.request.user.is_company_admin()):
            raise PermissionError("Seuls les administrateurs peuvent créer des rôles")
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Mise à jour (admin seulement)"""
        if not (self.request.user.is_superuser or self.request.user.is_company_admin()):
            raise PermissionError("Seuls les administrateurs peuvent modifier des rôles")
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Suppression (admin seulement)"""
        if not (self.request.user.is_superuser or self.request.user.is_company_admin()):
            raise PermissionError("Seuls les administrateurs peuvent supprimer des rôles")
        
        # Empêcher la suppression des rôles système
        if instance.is_system:
            raise PermissionError("Impossible de supprimer un rôle système")
        
        return super().perform_destroy(instance)
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """
        POST /roles/{id}/assign-permissions/
        
        Assigne des permissions à un rôle
        Body: {"permission_ids": [1, 2, 3], "is_granted": true}
        """
        role = self.get_object()
        serializer = RolePermissionAssignmentSerializer(
            data=request.data,
            context={'role': role}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Permissions assignées avec succès',
                'role': role.display_name,
                'permissions_count': len(serializer.validated_data['permission_ids']),
                'is_granted': serializer.validated_data['is_granted']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        GET /roles/{id}/users/
        
        Utilisateurs ayant ce rôle
        """
        role = self.get_object()
        user_roles = role.user_assignments.select_related('user').filter(
            user__is_active=True
        )
        
        users_data = []
        for user_role in user_roles:
            users_data.append({
                'id': user_role.user.id,
                'username': user_role.user.username,
                'email': user_role.user.email,
                'first_name': user_role.user.first_name,
                'last_name': user_role.user.last_name,
                'company': user_role.user.company.name if user_role.user.company else None,
                'granted_at': user_role.granted_at,
                'expires_at': user_role.expires_at,
                'is_active': user_role.is_active(),
                'context': user_role.get_context_summary()
            })
        
        return Response({
            'role': role.display_name,
            'users_count': len(users_data),
            'users': users_data
        })
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """
        GET /roles/{id}/permissions/
        
        Permissions de ce rôle
        """
        role = self.get_object()
        role_permissions = role.role_permissions.select_related('permission').all()
        
        permissions_data = []
        for role_permission in role_permissions:
            permissions_data.append({
                'id': role_permission.permission.id,
                'name': role_permission.permission.display_name,
                'permission_type': role_permission.permission.permission_type,
                'resource_type': role_permission.permission.resource_type,
                'is_granted': role_permission.is_granted,
                'created_at': role_permission.created_at
            })
        
        return Response({
            'role': role.display_name,
            'permissions_count': len(permissions_data),
            'permissions': permissions_data
        })

class PermissionViewSet(AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des permissions
    
    Endpoints:
    - GET /permissions/ - Liste des permissions
    - GET /permissions/{id}/ - Détail d'une permission
    - GET /permissions/{id}/roles/ - Rôles avec cette permission
    """
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['permission_type', 'resource_type', 'is_active']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['name', 'display_name', 'permission_type', 'resource_type']
    ordering = ['resource_type', 'permission_type', 'name']
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        # Tous les utilisateurs peuvent voir les permissions actives
        return super().get_queryset().filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """
        GET /permissions/{id}/roles/
        
        Rôles ayant cette permission
        """
        permission = self.get_object()
        role_permissions = permission.permission_roles.select_related('role').filter(
            is_granted=True,
            role__is_active=True
        )
        
        roles_data = []
        for role_permission in role_permissions:
            roles_data.append({
                'id': role_permission.role.id,
                'name': role_permission.role.display_name,
                'role_type': role_permission.role.role_type,
                'is_system': role_permission.role.is_system,
                'users_count': role_permission.role.user_assignments.count(),
                'assigned_at': role_permission.created_at
            })
        
        return Response({
            'permission': permission.display_name,
            'roles_count': len(roles_data),
            'roles': roles_data
        })

class UserRoleViewSet(BulkActionViewSetMixin, AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des assignations de rôles
    
    Endpoints:
    - GET /user-roles/ - Liste des assignations
    - POST /user-roles/ - Création d'assignation
    - GET /user-roles/{id}/ - Détail d'une assignation
    - PUT/PATCH /user-roles/{id}/ - Mise à jour d'une assignation
    - DELETE /user-roles/{id}/ - Suppression d'une assignation
    """
    
    queryset = UserRole.objects.select_related('user', 'role', 'company', 'brand', 'feature').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'role', 'company', 'brand', 'feature']
    search_fields = ['user__username', 'role__display_name', 'company__name', 'brand__name']
    ordering_fields = ['granted_at', 'expires_at', 'created_at']
    ordering = ['-granted_at']
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'create':
            return UserRoleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserRoleUpdateSerializer
        return UserRoleSerializer
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Superuser voit tout
        if user.is_superuser:
            return queryset
        
        # Company admin voit son entreprise
        if user.is_company_admin():
            return queryset.filter(
                Q(user__company=user.company) | 
                Q(company=user.company)
            )
        
        # Autres utilisateurs voient seulement leurs propres rôles
        return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """Création avec assignation automatique"""
        # Assigner automatiquement granted_by
        serializer.save(granted_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        GET /user-roles/by-user/
        
        Rôles groupés par utilisateur
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(user_id=user_id)
        
        # Grouper par contexte
        roles_by_context = {}
        for user_role in queryset:
            context = f"{user_role.role.role_type}"
            if user_role.company:
                context += f" - {user_role.company.name}"
            if user_role.brand:
                context += f" - {user_role.brand.name}"
            if user_role.feature:
                context += f" - {user_role.feature.display_name}"
            
            if context not in roles_by_context:
                roles_by_context[context] = []
            roles_by_context[context].append(
                UserRoleSerializer(user_role).data
            )
        
        return Response({
            'user_id': user_id,
            'roles_by_context': roles_by_context,
            'total_roles': queryset.count(),
            'active_roles': sum(1 for ur in queryset if ur.is_active())
        })
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """
        GET /user-roles/by-role/
        
        Assignations groupées par rôle
        """
        role_id = request.query_params.get('role_id')
        if not role_id:
            return Response(
                {'error': 'role_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(role_id=role_id)
        
        # Grouper par entreprise
        assignments_by_company = {}
        for user_role in queryset:
            company_name = user_role.company.name if user_role.company else 'Global'
            if company_name not in assignments_by_company:
                assignments_by_company[company_name] = []
            assignments_by_company[company_name].append(
                UserRoleSerializer(user_role).data
            )
        
        return Response({
            'role_id': role_id,
            'assignments_by_company': assignments_by_company,
            'total_assignments': queryset.count(),
            'active_assignments': sum(1 for ur in queryset if ur.is_active())
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        GET /user-roles/expiring-soon/
        
        Rôles expirant prochainement
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Rôles expirant dans les 30 jours
        expiring_date = timezone.now() + timedelta(days=30)
        expiring_roles = self.get_queryset().filter(
            expires_at__lte=expiring_date,
            expires_at__gt=timezone.now()
        ).order_by('expires_at')
        
        return Response({
            'expiring_roles_count': expiring_roles.count(),
            'expiring_roles': UserRoleSerializer(expiring_roles, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def user_permissions_overview(self, request):
        """
        GET /user-roles/user-permissions-overview/
        
        Vue d'ensemble des permissions par utilisateur
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users_core.models.user import CustomUser
        try:
            user = CustomUser.objects.get(id=user_id)
            overview = UserPermissionsOverviewSerializer(user).data
            return Response(overview)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Utilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def roles_overview(self, request):
        """
        GET /user-roles/roles-overview/
        
        Vue d'ensemble des rôles et assignations
        """
        queryset = self.get_queryset()
        
        # Statistiques globales
        total_assignments = queryset.count()
        active_assignments = sum(1 for ur in queryset if ur.is_active())
        
        # Répartition par rôle
        assignments_by_role = queryset.values('role__display_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Répartition par type de rôle
        assignments_by_type = queryset.values('role__role_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'activation_rate': (active_assignments / total_assignments * 100) if total_assignments > 0 else 0,
            'assignments_by_role': list(assignments_by_role),
            'assignments_by_type': list(assignments_by_type)
        })
