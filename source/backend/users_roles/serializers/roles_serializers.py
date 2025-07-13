# backend/users_roles/serializers/roles_serializers.py
from rest_framework import serializers
from users_roles.models.roles import Role, UserRole, Permission, RolePermission

class RoleSerializer(serializers.ModelSerializer):
    """Serializer pour Role"""
    
    users_count = serializers.SerializerMethodField()
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'display_name', 'description', 'role_type',
            'is_active', 'is_system', 'users_count', 'permissions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_users_count(self, obj):
        """Nombre d'utilisateurs avec ce rôle"""
        return obj.user_assignments.count()
    
    def get_permissions_count(self, obj):
        """Nombre de permissions associées"""
        return obj.role_permissions.filter(is_granted=True).count()
    
    def validate_name(self, value):
        """Validation du nom du rôle"""
        if self.instance:
            # Lors de la mise à jour, vérifier l'unicité sauf pour l'instance actuelle
            if Role.objects.filter(name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ce nom de rôle existe déjà")
        else:
            # Lors de la création, vérifier l'unicité
            if Role.objects.filter(name=value).exists():
                raise serializers.ValidationError("Ce nom de rôle existe déjà")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    """Serializer pour Permission"""
    
    roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'display_name', 'description', 'permission_type',
            'resource_type', 'is_active', 'roles_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_roles_count(self, obj):
        """Nombre de rôles avec cette permission"""
        return obj.permission_roles.filter(is_granted=True).count()

class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer pour RolePermission"""
    
    role_name = serializers.CharField(source='role.display_name', read_only=True)
    permission_name = serializers.CharField(source='permission.display_name', read_only=True)
    permission_type = serializers.CharField(source='permission.permission_type', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_name', 'permission', 'permission_name',
            'permission_type', 'is_granted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer pour UserRole"""
    
    # Informations utilisateur
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    # Informations rôle
    role_name = serializers.CharField(source='role.display_name', read_only=True)
    role_type = serializers.CharField(source='role.role_type', read_only=True)
    
    # Informations contexte
    company_name = serializers.CharField(source='company.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    feature_name = serializers.CharField(source='feature.display_name', read_only=True)
    
    # Informations sur qui a accordé le rôle
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True)
    
    # Champs calculés
    is_active_status = serializers.SerializerMethodField()
    context_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_username', 'user_email',
            'role', 'role_name', 'role_type',
            'company', 'company_name', 'brand', 'brand_name',
            'feature', 'feature_name',
            'granted_by', 'granted_by_username', 'granted_at', 'expires_at',
            'is_active_status', 'context_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['granted_at', 'created_at', 'updated_at']
    
    def get_is_active_status(self, obj):
        """Statut d'activation du rôle"""
        return obj.is_active()
    
    def get_context_summary(self, obj):
        """Résumé du contexte"""
        return obj.get_context_summary()
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier la cohérence du contexte
        role = data.get('role')
        company = data.get('company')
        brand = data.get('brand')
        feature = data.get('feature')
        
        if role:
            # Vérifier que le contexte correspond au type de rôle
            if role.role_type == 'company' and not company:
                raise serializers.ValidationError("Un rôle de type 'company' nécessite un contexte company")
            
            if role.role_type == 'brand' and not brand:
                raise serializers.ValidationError("Un rôle de type 'brand' nécessite un contexte brand")
            
            if role.role_type == 'feature' and not feature:
                raise serializers.ValidationError("Un rôle de type 'feature' nécessite un contexte feature")
        
        # Vérifier que la brand appartient à la company si les deux sont spécifiés
        if company and brand:
            if brand.company != company:
                raise serializers.ValidationError("La marque doit appartenir à l'entreprise spécifiée")
        
        return data

class UserRoleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une assignation de rôle"""
    
    class Meta:
        model = UserRole
        fields = [
            'user', 'role', 'company', 'brand', 'feature',
            'granted_by', 'expires_at'
        ]
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier qu'il n'y a pas déjà une assignation identique
        existing = UserRole.objects.filter(
            user=data['user'],
            role=data['role'],
            company=data.get('company'),
            brand=data.get('brand'),
            feature=data.get('feature')
        ).exists()
        
        if existing:
            raise serializers.ValidationError("Cette assignation de rôle existe déjà")
        
        return super().validate(data)

class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une assignation de rôle"""
    
    class Meta:
        model = UserRole
        fields = ['expires_at']

class RolePermissionAssignmentSerializer(serializers.Serializer):
    """Serializer pour assigner des permissions à un rôle"""
    
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs des permissions à assigner"
    )
    is_granted = serializers.BooleanField(
        default=True,
        help_text="Permissions accordées ou refusées"
    )
    
    def validate_permission_ids(self, value):
        """Valide les IDs des permissions"""
        if not value:
            raise serializers.ValidationError("Au moins une permission doit être sélectionnée")
        
        # Vérifier que toutes les permissions existent
        permissions = Permission.objects.filter(id__in=value, is_active=True)
        if permissions.count() != len(value):
            raise serializers.ValidationError("Certaines permissions n'existent pas ou ne sont pas actives")
        
        return value
    
    def save(self):
        """Assigne les permissions au rôle"""
        role = self.context['role']
        permission_ids = self.validated_data['permission_ids']
        is_granted = self.validated_data['is_granted']
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        
        # Créer ou mettre à jour les assignations
        for permission in permissions:
            role_permission, created = RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
                defaults={'is_granted': is_granted}
            )
            if not created:
                role_permission.is_granted = is_granted
                role_permission.save()
        
        return role

class UserPermissionsOverviewSerializer(serializers.Serializer):
    """Serializer pour une vue d'ensemble des permissions d'un utilisateur"""
    
    user_id = serializers.IntegerField()
    user_username = serializers.CharField()
    user_email = serializers.CharField()
    total_roles = serializers.IntegerField()
    active_roles = serializers.IntegerField()
    total_permissions = serializers.IntegerField()
    permissions_by_type = serializers.DictField()
    
    def to_representation(self, user):
        """Calcule les permissions pour un utilisateur"""
        user_roles = user.user_roles.all()
        active_roles = [ur for ur in user_roles if ur.is_active()]
        
        # Collecter toutes les permissions
        all_permissions = set()
        for user_role in active_roles:
            role_permissions = user_role.role.role_permissions.filter(is_granted=True)
            all_permissions.update(rp.permission for rp in role_permissions)
        
        # Grouper par type
        permissions_by_type = {}
        for permission in all_permissions:
            ptype = permission.permission_type
            if ptype not in permissions_by_type:
                permissions_by_type[ptype] = []
            permissions_by_type[ptype].append(permission.display_name)
        
        return {
            'user_id': user.id,
            'user_username': user.username,
            'user_email': user.email,
            'total_roles': user_roles.count(),
            'active_roles': len(active_roles),
            'total_permissions': len(all_permissions),
            'permissions_by_type': permissions_by_type,
        }
