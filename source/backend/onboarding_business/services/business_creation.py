# backend/onboarding_business/services/business_creation.py

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import logging

from company_core.models import Company
from brands_core.models import Brand
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def create_solo_business_for_user(user, business_name=None):
    """
    Crée un business solo pour un user (Company + Brand + User assignment)
    
    Args:
        user (CustomUser): User pour qui créer le business
        business_name (str, optional): Nom du business
        
    Returns:
        dict: {'company': Company, 'brand': Brand}
    """
    if not business_name:
        business_name = f"Business de {user.first_name or user.username}"
    
    try:
        with transaction.atomic():
            # 1. Créer Company avec trial automatique (2 semaines)
            company = Company.objects.create(
                name=business_name,
                admin=user,
                billing_email=user.email,
                trial_expires_at=timezone.now() + timedelta(weeks=2)
            )
            
            # 2. Assigner user à la company
            user.company = company
            user.user_type = 'agency_admin'  # Solo business owner = agency_admin
            user.save(update_fields=['company', 'user_type'])
            
            # 3. Créer Brand par défaut
            brand_name = f"Brand {company.name}"
            brand = Brand.objects.create(
                company=company,
                name=brand_name,
                brand_admin=user
            )
            
            # 4. Assigner user à la brand (M2M)
            brand.users.add(user)
            
            logger.info(f"Solo business créé: {company.name} (Company: {company.id}, Brand: {brand.id})")
            
            return {
                'company': company,
                'brand': brand
            }
            
    except Exception as e:
        logger.error(f"Erreur création solo business pour {user.username}: {str(e)}", exc_info=True)
        raise


def get_business_creation_summary(user):
    """
    Résumé complet de la création business pour un user
    
    Args:
        user (CustomUser): User à analyser
        
    Returns:
        dict: Résumé complet
    """
    has_business = hasattr(user, 'company') and user.company is not None
    
    if not has_business:
        return {
            'user_id': user.id,
            'username': user.username,
            'has_business': False,
            'is_eligible_for_business': not has_business and user.is_active,
            'onboarding_complete': False,
            'business_summary': None
        }
    
    company = user.company
    brands = company.brands.filter(is_deleted=False)
    
    return {
        'user_id': user.id,
        'username': user.username,
        'has_business': True,
        'is_eligible_for_business': False,  # A déjà un business
        'onboarding_complete': True,
        'business_summary': {
            'company': {
                'id': company.id,
                'name': company.name,
                'business_mode': company.get_business_mode(),
                'is_trial': company.is_in_trial(),
                'trial_days_remaining': company.trial_days_remaining(),
                'created_at': company.created_at
            },
            'brands': [
                {
                    'id': brand.id,
                    'name': brand.name,
                    'is_admin': brand.brand_admin == user,
                    'users_count': brand.users.filter(is_active=True).count()
                }
                for brand in brands
            ],
            'stats': company.get_stats_summary(),
            'permissions': user.get_permissions_summary()
        }
    }