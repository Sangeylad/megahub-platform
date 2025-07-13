# backend/public_tools/utils/security.py
import hashlib
import secrets
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def generate_secure_token(length=32):
    """
    Génère un token sécurisé
    """
    return secrets.token_urlsafe(length)

def hash_ip_address(ip_address):
    """
    Hash sécurisé d'une adresse IP pour les logs
    """
    salt = settings.SECRET_KEY[:16]
    return hashlib.sha256(f"{salt}{ip_address}".encode()).hexdigest()[:16]

def is_rate_limited(identifier, limit_per_hour=100):
    """
    Vérification de rate limiting personnalisée
    """
    cache_key = f"rate_limit_{identifier}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit_per_hour:
        logger.warning(f"Rate limit dépassé pour {hash_ip_address(identifier)}")
        return True
    
    # Incrémente le compteur
    cache.set(cache_key, current_count + 1, timeout=3600)  # 1 heure
    return False

def sanitize_filename(filename):
    """
    Nettoie un nom de fichier pour éviter les attaques
    """
    import re
    # Garde seulement alphanumerique, points, tirets et underscores
    clean_name = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Limite la longueur
    return clean_name[:100]