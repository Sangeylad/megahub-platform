# backend/common/middleware/brand_middleware.py

import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request

logger = logging.getLogger(__name__)

class BrandContextMiddleware(MiddlewareMixin):
    """
    Middleware qui force l'authentification JWT DRF
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Force l'authentification JWT avant de définir la brand
        """
        print(f"🔍 === BRAND MIDDLEWARE process_view ===")
        print(f"🔍 Path: {request.path}")
        print(f"🔍 Method: {request.method}")
        
        # Initialiser current_brand
        request.current_brand = None
        
        # Vérifier si c'est une API DRF (commence par /api/ ou pas de static)
        if not self._is_api_request(request):
            print(f"🔍 Non-API request, skipping")
            return None
        
        # Force l'authentification JWT DRF
        try:
            # Créer un Request DRF à partir du request Django
            drf_request = Request(request)
            
            # Essayer d'authentifier avec JWT
            auth_result = self.jwt_authenticator.authenticate(drf_request)
            
            if auth_result:
                user, token = auth_result
                request.user = user
                print(f"🔍 JWT Authenticated user: {user} (ID: {user.id})")
            else:
                print(f"🔍 No JWT token found or invalid")
                return None
                
        except Exception as e:
            print(f"❌ JWT Authentication error: {str(e)}")
            return None
        
        # Maintenant que l'user est authentifié, définir la brand
        if not request.user.is_authenticated:
            print(f"❌ User still not authenticated after JWT")
            return None
        
        user = request.user
        print(f"🔍 Processing brand for user: {user}")
        
        # 1. Brand depuis header X-Brand-ID
        brand_header = request.META.get('HTTP_X_BRAND_ID')
        print(f"🔍 X-Brand-ID header: {brand_header}")
        
        if brand_header:
            try:
                from brands_core.models import Brand
                brand = Brand.objects.get(id=brand_header)
                print(f"🔍 Brand found: {brand.name} (ID: {brand.id})")
                
                # Vérifier accès user à cette brand
                if self._user_has_brand_access(user, brand):
                    request.current_brand = brand
                    print(f"✅ Brand set from header: {brand.name} (ID: {brand.id})")
                    return None
                else:
                    print(f"❌ User {user.id} denied access to brand {brand_header}")
            except Exception as e:
                print(f"❌ Error loading brand {brand_header}: {str(e)}")
        
        # 2. Fallback automatique
        fallback_brand = self._get_fallback_brand(user)
        if fallback_brand:
            request.current_brand = fallback_brand
            print(f"✅ Brand set from fallback: {fallback_brand.name} (ID: {fallback_brand.id})")
        else:
            print(f"❌ No brand available for user {user.id}")
        
        print(f"🔍 === BRAND MIDDLEWARE process_view END ===")
        return None
    
    def _is_api_request(self, request):
        """Détermine si c'est une requête API"""
        path = request.path
        
        # Exclure les ressources statiques
        if any(path.startswith(prefix) for prefix in ['/static/', '/media/', '/admin/']):
            return False
        
        # Inclure toutes les autres requêtes (ton API est à la racine)
        return True
    
    def _user_has_brand_access(self, user, brand):
        """Vérifie si user a accès à la brand"""
        print(f"🔍 Checking brand access for user {user.id} to brand {brand.id}")
        
        # Company admin : accès total
        if hasattr(user, 'is_company_admin') and user.is_company_admin():
            print(f"✅ User is company admin - access granted")
            return True
        
        # User normal : vérifier brands accessibles
        if hasattr(user, 'brands') and user.brands.filter(id=brand.id).exists():
            print(f"✅ User has direct access to brand")
            return True
        
        print(f"❌ User has no access to brand")
        return False
    
    def _get_fallback_brand(self, user):
        """Récupère brand de fallback selon user"""
        print(f"🔍 Getting fallback brand for user {user.id}")
        
        # Company admin : première brand du système
        if hasattr(user, 'is_company_admin') and user.is_company_admin():
            from brands_core.models import Brand
            first_brand = Brand.objects.first()
            if first_brand:
                print(f"✅ Fallback for admin: {first_brand.name}")
                return first_brand
        
        # User normal : première brand accessible
        if hasattr(user, 'brands') and user.brands.exists():
            first_brand = user.brands.first()
            print(f"✅ Fallback for user: {first_brand.name}")
            return first_brand
        
        print(f"❌ No fallback brand available")
        return None