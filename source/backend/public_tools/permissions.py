# backend/public_tools/permissions.py
from rest_framework.permissions import BasePermission
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PublicToolsOnly(BasePermission):
    """
    Permission qui INTERDIT l'accès aux données privées de MegaHub.
    Autorise UNIQUEMENT les endpoints public_tools.
    """
    
    def has_permission(self, request, view):
        # Log de sécurité
        logger.info(f"Public tools access from {request.META.get('REMOTE_ADDR')} - {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
        
        # Vérification que c'est bien un endpoint public_tools
        if not hasattr(view, 'action') and not request.resolver_match:
            return False
            
        # Vérification du namespace
        if request.resolver_match and request.resolver_match.namespace != 'public_tools':
            logger.warning(f"Tentative d'accès non autorisée depuis public tools: {request.path}")
            return False
            
        return True

class WordPressDomainOnly(BasePermission):
    """
    Permission qui autorise uniquement les calls depuis le domaine WordPress
    """
    
    def has_permission(self, request, view):
        allowed_origins = [
            'https://humari.fr',
            'https://www.humari.fr',
        ]
        
        # En développement, autoriser localhost
        if settings.DEBUG:
            allowed_origins.extend([
                'http://localhost',
                'http://127.0.0.1',
            ])
        
        origin = request.META.get('HTTP_ORIGIN')
        referer = request.META.get('HTTP_REFERER')
        
        # Vérifier origin ou referer
        if origin:
            return any(origin.startswith(domain) for domain in allowed_origins)
        elif referer:
            return any(referer.startswith(domain) for domain in allowed_origins)
        
        # Autoriser les calls directs en dev
        if settings.DEBUG:
            return True
            
        logger.warning(f"Call non autorisé - Origin: {origin}, Referer: {referer}")
        return False