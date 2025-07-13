# backend/glossary/throttling.py
from rest_framework.throttling import AnonRateThrottle


class GlossaryReadThrottle(AnonRateThrottle):
    """
    Rate limiting pour la lecture du glossaire (catégories, termes)
    Plus permissif car c'est de la consultation
    """
    scope = 'glossary_read'
    
    def get_cache_key(self, request, view):
        # Rate limit par IP
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class GlossarySearchThrottle(AnonRateThrottle):
    """
    Rate limiting plus strict pour les recherches
    Évite les abus sur les endpoints de recherche
    """
    scope = 'glossary_search'
    
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        # Ajouter le type d'action pour un rate limit par type
        action = getattr(view, 'action', 'unknown')
        return f"glossary_search_{action}_{ident}"


class GlossaryStatsThrottle(AnonRateThrottle):
    """
    Rate limiting pour les endpoints de stats
    Plus restrictif car calculs potentiellement coûteux
    """
    scope = 'glossary_stats'
    
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return f"glossary_stats_{ident}"