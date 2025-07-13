# backend/onboarding_trials/services/auto_upgrade.py
from django.db import transaction
import logging

from ..models import TrialEvent
from .trial import create_trial_event 

logger = logging.getLogger(__name__)

def check_auto_upgrade_trigger(company, triggered_by=None):
    """
    Vérifie et déclenche upgrade automatique solo → agency
    
    Args:
        company (Company): Company à vérifier
        triggered_by (CustomUser): User déclencheur
        
    Returns:
        bool: True si upgrade déclenché
    """
    if not company.is_agency():
        return False
    
    # Vérifier si déjà upgradé
    if company.trial_events.filter(event_type='auto_upgrade').exists():
        logger.debug(f"Company {company.name} déjà upgradée")
        return False
    
    brands_count = company.brands.filter(is_deleted=False).count()
    
    with transaction.atomic():
        # Event auto-upgrade
        create_trial_event(
            company=company,
            event_type='auto_upgrade',
            event_data={
                'from_mode': 'solo',
                'to_mode': 'agency',
                'brands_count': brands_count,
                'trigger': 'second_brand_created'
            },
            triggered_by=triggered_by
        )
        
        # Logique upgrade
        handle_agency_upgrade(company)
        
        logger.info(f"Auto-upgrade déclenché pour {company.name}: {brands_count} brands")
        
        return True

def handle_agency_upgrade(company):
    """
    Gère l'upgrade vers mode agency
    
    Args:
        company (Company): Company à upgrader
    """
    # Upgrade slots users (de 1 à 5)
    from onboarding_business.services.slots_setup import upgrade_slots_for_agency
    upgrade_slots_for_agency(company, new_users_limit=5)
    
    # Integration billing pour upgrade plan
    from .billing_integration import handle_agency_upgrade_billing
    handle_agency_upgrade_billing(company)
    
    logger.info(f"Agency upgrade traité pour {company.name}")

def trigger_manual_upgrade(company, plan_type, triggered_by):
    """
    Déclenche upgrade manuel
    
    Args:
        company (Company): Company à upgrader
        plan_type (str): Type de plan choisi
        triggered_by (CustomUser): User déclencheur
        
    Returns:
        bool: True si upgrade réussi
    """
    try:
        with transaction.atomic():
            # Event manual upgrade
            create_trial_event(
                company=company,
                event_type='manual_upgrade',
                event_data={
                    'plan_type': plan_type,
                    'previous_mode': company.get_business_mode(),
                    'brands_count': company.brands.filter(is_deleted=False).count()
                },
                triggered_by=triggered_by
            )
            
            # Integration billing
            from .billing_integration import handle_manual_upgrade_billing
            handle_manual_upgrade_billing(company, plan_type)
            
            logger.info(f"Manual upgrade déclenché pour {company.name}: {plan_type}")
            
            return True
            
    except Exception as e:
        logger.error(f"Erreur manual upgrade {company.name}: {str(e)}")
        return False

def get_upgrade_opportunities():
    """
    Identifie les companies candidates pour upgrade
    
    Returns:
        dict: Opportunities d'upgrade
    """
    from company_core.models import Company
    
    # Solo businesses en trial
    solo_in_trial = Company.objects.filter(
        is_active=True,
        trial_expires_at__isnull=False
    ).filter(
        brands__is_deleted=False
    ).annotate(
        brands_count=models.Count('brands', filter=models.Q(brands__is_deleted=False))
    ).filter(brands_count=1)
    
    # Agencies pas encore upgradées
    auto_upgrade_candidates = Company.objects.filter(
        is_active=True
    ).annotate(
        brands_count=models.Count('brands', filter=models.Q(brands__is_deleted=False))
    ).filter(brands_count__gte=2).exclude(
        trial_events__event_type='auto_upgrade'
    )
    
    return {
        'solo_in_trial': solo_in_trial.count(),
        'auto_upgrade_candidates': auto_upgrade_candidates.count(),
        'total_opportunities': solo_in_trial.count() + auto_upgrade_candidates.count()
    }
