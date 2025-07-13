# backend/common/permissions/business_permissions.py

from rest_framework import permissions
from .base_permissions import (
    HeaderBasedScopePermission, AdminPermission, 
    BaseResourcePermission, OwnershipPermission
)
from .mixins import AdminBypassMixin, ScopeValidationMixin


class IsCompanyAdmin(AdminPermission):
    """
    Permission pour administrateurs de company
    Utilisable dans toutes les apps
    """
    admin_method = 'is_company_admin'


class IsBrandAdmin(BaseResourcePermission, AdminBypassMixin):
    """
    Permission pour administrateurs de brand
    Vérifie brand_admin ou company_admin
    """
    
    def get_resource_from_view(self, view):
        """Récupère la brand depuis current_brand du middleware"""
        # 🆕 NOUVEAU : D'abord depuis le middleware
        request = view.request if hasattr(view, 'request') else None
        if request and hasattr(request, 'current_brand') and request.current_brand:
            return request.current_brand
            
        # Fallback sur kwargs pour routes spécifiques /brands/{id}/
        brand_id = view.kwargs.get('brand_id') or view.kwargs.get('pk')
        if brand_id:
            try:
                from brands_core.models import Brand
                return Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                return None
        return None
    
    def user_has_access_to_resource(self, user, brand):
        """Vérifie si user est admin de la brand"""
        # Company admin bypass
        if self._user_is_admin(user):
            return True
        
        # Brand admin
        return brand.brand_admin == user


class IsBrandMember(permissions.BasePermission):
    """
    Permission pour membres d'une brand
    🆕 UTILISE LE MIDDLEWARE current_brand
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Company admin bypass
        if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin():
            return True
        
        # 🆕 MIDDLEWARE : Si current_brand existe, c'est que l'user y a accès
        if hasattr(request, 'current_brand') and request.current_brand:
            return True
        
        # ⚠️ Si pas de current_brand, c'est que le middleware n'a pas pu définir de brand
        # Donc l'user n'a accès à aucune brand
        return False
    
    def has_object_permission(self, request, view, obj):
        """Vérifie que l'objet appartient à la brand courante"""
        if not request.user.is_authenticated:
            return False
        
        # Company admin bypass
        if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin():
            return True
        
        # 🆕 Vérifier que l'objet appartient à current_brand
        if hasattr(request, 'current_brand') and request.current_brand:
            return self._object_belongs_to_brand(obj, request.current_brand)
        
        return False
    
    def _object_belongs_to_brand(self, obj, brand):
        """Vérifie qu'un objet appartient à la brand courante"""
        obj_brand_id = self._get_brand_from_object(obj)
        return obj_brand_id == brand.id if obj_brand_id else False
    
    def _get_brand_from_object(self, obj):
        """Extrait brand_id depuis une instance d'objet"""
        # Direct brand
        if hasattr(obj, 'brand_id'):
            return obj.brand_id
        elif hasattr(obj, 'brand'):
            return obj.brand.id
        
        # Via website
        elif hasattr(obj, 'website') and hasattr(obj.website, 'brand_id'):
            return obj.website.brand_id
        elif hasattr(obj, 'website') and hasattr(obj.website, 'brand'):
            return obj.website.brand.id
        
        # Via page → website → brand
        elif hasattr(obj, 'page'):
            if hasattr(obj.page, 'website') and hasattr(obj.page.website, 'brand_id'):
                return obj.page.website.brand_id
            elif hasattr(obj.page, 'website') and hasattr(obj.page.website, 'brand'):
                return obj.page.website.brand.id
        
        # Via article → page → website → brand (blog)
        elif hasattr(obj, 'article'):
            if hasattr(obj.article, 'page') and hasattr(obj.article.page, 'website'):
                return obj.article.page.website.brand_id
        
        # Via collection (blog)
        elif hasattr(obj, 'collection') and hasattr(obj.collection, 'brand'):
            return obj.collection.brand_id
        
        return None


class IsBrandOwner(BaseResourcePermission, AdminBypassMixin):
    """
    Permission pour propriétaires de brand (brand_admin uniquement)
    Plus restrictif que IsBrandAdmin
    """
    
    def get_resource_from_view(self, view):
        # Utilise current_brand du middleware
        request = view.request if hasattr(view, 'request') else None
        if request and hasattr(request, 'current_brand'):
            return request.current_brand
        return None
    
    def user_has_access_to_resource(self, user, brand):
        # Seul le brand admin (PAS company admin)
        return brand.brand_admin == user if brand else False


class IsWebsiteMember(permissions.BasePermission):
    """
    Permission pour accès à un website
    Vérifie via current_brand du middleware
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Company admin bypass
        if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin():
            return True
        
        # 🆕 Si current_brand définie, vérifier le website
        if hasattr(request, 'current_brand') and request.current_brand:
            website_id = view.kwargs.get('website_id') or view.kwargs.get('pk')
            if website_id:
                try:
                    from seo_websites_core.models import Website
                    website = Website.objects.get(id=website_id)
                    return website.brand_id == request.current_brand.id
                except:
                    return False
            # Si pas de website_id, on fait confiance à current_brand
            return True
        
        return False


class IsAuthorOrAdmin(OwnershipPermission):
    """
    Permission pour auteurs de contenu + admin
    Réutilisable pour blog, articles, etc.
    """
    owner_field = 'primary_author.user'  # Navigation dans les relations
    allow_admin_override = True
    admin_method = 'is_company_admin'


class IsBlogAuthor(permissions.BasePermission):
    """
    Permission spécifique pour auteurs de blog
    Vérifie aussi current_brand
    """
    
    def has_permission(self, request, view):
        """Vérifie d'abord l'accès brand via middleware"""
        if not IsBrandMember().has_permission(request, view):
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Company admin bypass
        if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin():
            return True
        
        # Vérifier que l'objet appartient à current_brand
        if not IsBrandMember().has_object_permission(request, view, obj):
            return False
        
        # Vérifier si user est l'auteur
        if hasattr(obj, 'primary_author'):
            return obj.primary_author.user == request.user
        
        # Pour BlogAuthor objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class ReadOnlyOrBrandMember(permissions.BasePermission):
    """
    Lecture pour tous, écriture pour membres de brand
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Pour écriture, vérifier membership brand via middleware
        return IsBrandMember().has_permission(request, view)


class DynamicBrandPermission(permissions.BasePermission):
    """
    Permission dynamique selon l'action et la brand
    Configurable par ViewSet
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        action = getattr(view, 'action', None)
        permission_config = getattr(view, 'brand_permissions', {})
        
        required_permission = permission_config.get(action, 'member')
        
        if required_permission == 'admin':
            return IsBrandAdmin().has_permission(request, view)
        elif required_permission == 'member':
            return IsBrandMember().has_permission(request, view)
        elif required_permission == 'company_admin':
            return IsCompanyAdmin().has_permission(request, view)
        
        return False


# Aliases pour compatibilité et imports simplifiés
IsBrandMemberPermission = IsBrandMember
IsCompanyAdminPermission = IsCompanyAdmin  
IsBrandAdminPermission = IsBrandAdmin
IsAuthenticated = permissions.IsAuthenticated  # Réexport pour imports simplifiés


# 🆕 HELPER pour debug
def check_current_brand(request):
    """Helper pour vérifier la brand courante dans les vues"""
    if hasattr(request, 'current_brand') and request.current_brand:
        return {
            'has_brand': True,
            'brand_id': request.current_brand.id,
            'brand_name': request.current_brand.name,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'is_admin': request.user.is_company_admin() if hasattr(request.user, 'is_company_admin') else False
        }
    return {
        'has_brand': False,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'reason': 'No brand set by middleware'
    }