# backend/common/permissions/mixins.py
from django.core.exceptions import ObjectDoesNotExist


class AdminBypassMixin:
    """
    Mixin pour bypass admin sur les permissions
    """
    admin_method = 'is_company_admin'
    allow_admin_bypass = True
    
    def _user_is_admin(self, user):
        """Vérifie si user est admin"""
        if not self.allow_admin_bypass:
            return False
        
        if self.admin_method and hasattr(user, self.admin_method):
            return getattr(user, self.admin_method)()
        
        return user.is_staff


class ScopeValidationMixin:
    """
    Mixin pour validation de scope depuis headers/kwargs
    """
    
    def _get_scope_from_request(self, request, view):
        """Récupère le scope depuis request (header ou kwargs)"""
        # Priorité aux headers
        for header_name in getattr(self, 'scope_headers', []):
            scope_value = request.headers.get(header_name)
            if scope_value:
                return scope_value
        
        # Puis les kwargs de la view
        for kwarg_name in getattr(self, 'scope_kwargs', []):
            scope_value = view.kwargs.get(kwarg_name)
            if scope_value:
                return scope_value
        
        return None
    
    def _validate_scope_access(self, user, scope_value, scope_model, user_relation):
        """Valide l'accès user au scope"""
        try:
            if not scope_value:
                return False
            
            # Vérifier que le scope existe
            scope_obj = scope_model.objects.get(id=scope_value)
            
            # Vérifier l'accès user
            return getattr(user, user_relation).filter(id=scope_value).exists()
        except ObjectDoesNotExist:
            return False
        except:
            return False


class CacheablePermissionMixin:
    """
    Mixin pour mise en cache des résultats de permissions
    """
    cache_timeout = 300  # 5 minutes par défaut
    
    def _get_cache_key(self, user, view, obj=None):
        """Génère une clé de cache pour la permission"""
        permission_name = self.__class__.__name__
        user_id = user.id if user.is_authenticated else 'anonymous'
        view_name = f"{view.__class__.__module__}.{view.__class__.__name__}"
        obj_key = f"{obj.__class__.__name__}_{obj.id}" if obj else 'no_obj'
        
        return f"permission:{permission_name}:{user_id}:{view_name}:{obj_key}"
    
    def _cache_permission_result(self, cache_key, result):
        """Met en cache le résultat"""
        # TODO: Implémentation avec Django cache framework
        pass
    
    def _get_cached_permission_result(self, cache_key):
        """Récupère depuis le cache"""
        # TODO: Implémentation avec Django cache framework
        return None


class AuditPermissionMixin:
    """
    Mixin pour audit des vérifications de permissions
    """
    
    def _log_permission_check(self, user, view, obj, result):
        """Log la vérification de permission"""
        # TODO: Implémentation logging structuré
        import logging
        logger = logging.getLogger('permissions')
        
        logger.info(
            f"Permission check: {self.__class__.__name__} "
            f"User={user.id if user.is_authenticated else 'anonymous'} "
            f"View={view.__class__.__name__} "
            f"Object={obj.__class__.__name__ if obj else None} "
            f"Result={result}"
        )