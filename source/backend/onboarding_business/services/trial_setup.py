# backend/onboarding_business/services/trial_setup.py

from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def setup_trial_subscription(company):
    """
    Setup subscription trial pour une company
    
    Args:
        company (Company): Company à configurer
        
    Returns:
        Subscription or None: Subscription créée ou None si billing non disponible
    """
    try:
        from billing_core.models import Plan, Subscription
        
        # Récupérer le plan starter par défaut
        try:
            starter_plan = Plan.objects.get(
                plan_type='starter',
                is_active=True
            )
        except Plan.DoesNotExist:
            logger.warning(f"Plan starter non trouvé pour trial {company.name}")
            return None
        
        # Créer subscription trial
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='trialing',
            started_at=timezone.now(),
            current_period_start=timezone.now(),
            current_period_end=company.trial_expires_at,
            trial_end=company.trial_expires_at,
            amount=starter_plan.price
        )
        
        logger.info(f"Trial subscription créée pour {company.name}")
        return subscription
        
    except ImportError:
        logger.info("billing_core non disponible - skip trial subscription")
        return None
    except Exception as e:
        logger.error(f"Erreur création trial subscription pour {company.name}: {str(e)}")
        return None


def extend_trial_period(company, additional_weeks=1):
    """
    Étend la période de trial
    
    Args:
        company (Company): Company concernée
        additional_weeks (int): Semaines supplémentaires
        
    Returns:
        bool: True si extension réussie
    """
    if not company.is_in_trial():
        logger.warning(f"Company {company.name} pas en trial - extension impossible")
        return False
    
    # Étendre company trial
    old_trial_end = company.trial_expires_at
    company.trial_expires_at = old_trial_end + timedelta(weeks=additional_weeks)
    company.save(update_fields=['trial_expires_at'])
    
    # Étendre subscription trial si existe
    try:
        from billing_core.models import Subscription
        subscription = company.subscription
        if subscription.is_trial():
            subscription.trial_end = company.trial_expires_at
            subscription.current_period_end = company.trial_expires_at
            subscription.save(update_fields=['trial_end', 'current_period_end'])
    except:
        pass  # Pas grave si subscription n'existe pas
    
    # Étendre features trial
    from .features_setup import extend_trial_features
    extend_trial_features(company, company.trial_expires_at)
    
    logger.info(f"Trial étendu pour {company.name}: +{additional_weeks} semaines")
    return True


def get_trial_summary(company):
    """
    Résumé du trial pour une company
    
    Args:
        company (Company): Company à analyser
        
    Returns:
        dict: Résumé trial
    """
    return {
        'is_trial': company.is_in_trial(),
        'trial_expires_at': company.trial_expires_at,
        'days_remaining': company.trial_days_remaining(),
        'can_extend': company.is_in_trial(),
        'subscription_status': getattr(company, 'subscription', {}).get('status') if hasattr(company, 'subscription') else None
    }