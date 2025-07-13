# mcp_server/authentication.py
import os
import logging
from typing import Dict, Any, Optional
from asgiref.sync import sync_to_async  # 🎯 Import correct

logger = logging.getLogger(__name__)

async def authenticate_request(arguments: Dict[str, Any]) -> int:
    """
    Authentifie une requête MCP et retourne le brand_id (async)
    """
    
    # En mode développement, utiliser brand_id par défaut
    if os.getenv('MCP_ENV') == 'development':
        default_brand_id = int(os.getenv('MCP_DEFAULT_BRAND_ID', '9'))  # Humari
        
        # Si brand_id fourni dans arguments, l'utiliser
        if 'brand_id' in arguments:
            provided_brand_id = int(arguments['brand_id'])
            logger.info(f"Using provided brand_id: {provided_brand_id}")
            return provided_brand_id
        
        logger.info(f"Using default brand_id: {default_brand_id}")
        return default_brand_id
    
    # En production, authentification plus stricte
    if 'brand_id' not in arguments:
        raise ValueError("brand_id is required")
    
    brand_id = int(arguments['brand_id'])
    
    # 🎯 Valider que la brand existe (avec sync_to_async)
    brand_exists = await sync_to_async(_check_brand_exists)(brand_id)
    if not brand_exists:
        raise ValueError(f"Brand {brand_id} not found")
    
    logger.info(f"Authenticated for brand_id: {brand_id}")
    return brand_id

def _check_brand_exists(brand_id: int) -> bool:
    """Vérifie l'existence d'une brand (fonction synchrone)"""
    try:
        from business.models import Brand
        Brand.objects.get(id=brand_id)
        return True
    except Exception:  # Brand.DoesNotExist ou import error
        return False

@sync_to_async
def get_brand_from_context(brand_id: int):
    """Récupère l'instance Brand depuis l'ID (async wrapper)"""
    from business.models import Brand
    return Brand.objects.get(id=brand_id)