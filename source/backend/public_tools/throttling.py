# backend/public_tools/throttling.py
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class PublicToolsAnonThrottle(AnonRateThrottle):
    """
    Rate limiting pour les utilisateurs anonymes des outils publics
    """
    scope = 'public_tools_anon'
    
    def get_cache_key(self, request, view):
        # Rate limit par IP
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class PublicToolsProcessThrottle(AnonRateThrottle):
    """
    Rate limiting plus strict pour les endpoints de traitement
    """
    scope = 'public_tools_process'
    
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        # Ajouter le type d'outil pour un rate limit par outil
        tool_type = getattr(view, 'tool_type', 'unknown')
        return f"public_tools_process_{tool_type}_{ident}"