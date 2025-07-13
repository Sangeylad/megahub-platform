# backend/onboarding_registration/services/validation.py
# onboarding_registration/services/validation.py
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def validate_user_eligibility(user):
    """
    Valide qu'un user peut créer un business automatiquement
    
    Args:
        user (CustomUser): User à valider
        
    Returns:
        bool: True si éligible pour business auto
    """
    # User déjà assigné à une company
    if user.company is not None:
        logger.debug(f"User {user.username} déjà assigné à company {user.company.name}")
        return False
    
    # User inactif
    if not user.is_active:
        logger.debug(f"User {user.username} inactif")
        return False
    
    # User superuser (admin platform)
    if user.is_superuser:
        logger.debug(f"User {user.username} est superuser")
        return False
    
    # User staff (admin platform)
    if user.is_staff:
        logger.debug(f"User {user.username} est staff")
        return False
    
    return True

def can_trigger_business_creation(user):
    """
    Vérifie si un user peut déclencher manuellement la création business
    
    Args:
        user (CustomUser): User demandeur
        
    Returns:
        bool: True si peut créer business
    """
    if not validate_user_eligibility(user):
        return False
    
    # Vérifier qu'il n'y a pas eu d'autres tentatives récentes
    # TODO: Ajouter logique anti-spam si nécessaire
    
    return True