# backend/common/permissions/base_permissions.py

from rest_framework import permissions
from abc import abstractmethod
from django.core.exceptions import ObjectDoesNotExist


class BaseResourcePermission(permissions.BasePermission):
    """
    Base abstraite pour permissions sur ressources
    Pattern réutilisable dans toutes les apps
    """
    
    @abstractmethod
    def get_resource_from_view(self, view):
        """Récupère la ressource depuis la view"""
        pass
    
    @abstractmethod
    def user_has_access_to_resource(self, user, resource):
        """Vérifie l'accès user à la ressource"""
        pass
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        resource = self.get_resource_from_view(view)
        if not resource:
            return False
        
        return self.user_has_access_to_resource(request.user, resource)
    
    def has_object_permission(self, request, view, obj):
        """Délègue à has_permission par défaut"""
        return self.has_permission(request, view)


class HeaderBasedScopePermission(permissions.BasePermission):
    """
    Permission basée sur un header de scope (X-Brand-Id, X-Tenant-Id, etc.)
    Réutilisable pour tous les systèmes de scope
    """
    header_name = None  # À override: 'X-Brand-Id'
    model_class = None  # À override: Brand
    user_relation_field = None  # À override: 'brands'
    admin_method = None  # À override: 'is_company_admin'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Super admin bypass
        if self._is_super_admin(request.user):
            return True
        
        # Vérifier scope dans header
        scope_id = request.headers.get(self.header_name)
        if not scope_id:
            return False
        
        return self._user_has_scope_access(request.user, scope_id)
    
    def _is_super_admin(self, user):
        """Vérifie si user est super admin"""
        if self.admin_method and hasattr(user, self.admin_method):
            return getattr(user, self.admin_method)()
        return user.is_staff
    
    def _user_has_scope_access(self, user, scope_id):
        """Vérifie l'accès au scope spécifique"""
        try:
            if self.user_relation_field:
                return getattr(user, self.user_relation_field).filter(
                    id=scope_id
                ).exists()
            return False
        except:
            return False


class AdminPermission(permissions.BasePermission):
    """
    Permission admin générique
    Configurable selon le type d'admin (company, brand, etc.)
    """
    admin_method = None  # À override: 'is_company_admin'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if self.admin_method and hasattr(request.user, self.admin_method):
            return getattr(request.user, self.admin_method)()
        
        return request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class OwnershipPermission(permissions.BasePermission):
    """
    Permission basée sur la propriété d'un objet
    Configurable selon le champ de propriété
    """
    owner_field = 'created_by'  # Champ propriétaire par défaut
    allow_admin_override = True  # Admin peut bypass
    admin_method = 'is_company_admin'  # Méthode admin par défaut
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin bypass
        if self.allow_admin_override and self._is_admin(request.user):
            return True
        
        # Vérifier propriété
        return self._user_owns_object(request.user, obj)
    
    def _is_admin(self, user):
        """Vérifie si user est admin"""
        if self.admin_method and hasattr(user, self.admin_method):
            return getattr(user, self.admin_method)()
        return user.is_staff
    
    def _user_owns_object(self, user, obj):
        """Vérifie si user possède l'objet"""
        try:
            # Navigation dans les relations (ex: 'blog_article.primary_author.user')
            owner_path = self.owner_field.split('.')
            current_obj = obj
            
            for path_part in owner_path:
                current_obj = getattr(current_obj, path_part, None)
                if current_obj is None:
                    return False
            
            return current_obj == user
        except:
            return False


class ReadOnlyOrAuthenticatedPermission(permissions.BasePermission):
    """
    Permission lecture pour tous, écriture pour authentifiés
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class ModelBasedPermission(permissions.BasePermission):
    """
    Permission basée sur un modèle spécifique
    Utilise les relations Django pour vérifier l'accès
    """
    model_class = None  # À override
    lookup_field = 'id'  # Champ de lookup
    user_filter = None  # Filtre pour vérifier l'accès user
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not self.model_class or not self.user_filter:
            return False
        
        # Récupérer l'ID depuis les kwargs de la view
        object_id = view.kwargs.get(f'{self.lookup_field}', 
                                  view.kwargs.get(f'{self.model_class.__name__.lower()}_{self.lookup_field}'))
        
        if not object_id:
            return True  # Pas d'objet spécifique, laisser passer
        
        try:
            # Vérifier que l'objet existe et que l'user y a accès
            filter_kwargs = {
                self.lookup_field: object_id,
                **self.user_filter(request.user)
            }
            return self.model_class.objects.filter(**filter_kwargs).exists()
        except:
            return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if not self.user_filter:
            return False
        
        try:
            filter_kwargs = self.user_filter(request.user)
            # Vérifier que l'objet respecte les critères user
            for field, value in filter_kwargs.items():
                obj_value = obj
                for field_part in field.split('__'):
                    obj_value = getattr(obj_value, field_part, None)
                    if obj_value is None:
                        return False
                
                if obj_value != value:
                    return False
            
            return True
        except:
            return False