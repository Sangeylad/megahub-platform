# backend/onboarding_trials/tasks.py
from celery import shared_task
import logging

from .services.trial import check_trial_warnings, check_expired_trials
from .services.auto_upgrade import get_upgrade_opportunities

logger = logging.getLogger(__name__)

@shared_task
def daily_trial_check():
    """
    Task quotidienne : Check warnings et expirations
    """
    try:
        warnings_sent = check_trial_warnings()
        expired_processed = check_expired_trials()
        
        logger.info(f"Daily trial check terminé: {warnings_sent} warnings, {expired_processed} expirés")
        
        return {
            'success': True,
            'warnings_sent': warnings_sent,
            'expired_processed': expired_processed
        }
        
    except Exception as e:
        logger.error(f"Erreur daily trial check: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def weekly_upgrade_analysis():
    """
    Task hebdomadaire : Analyse opportunities upgrade
    """
    try:
        opportunities = get_upgrade_opportunities()
        
        logger.info(f"Weekly upgrade analysis: {opportunities}")
        
        return {
            'success': True,
            'opportunities': opportunities
        }
        
    except Exception as e:
        logger.error(f"Erreur weekly upgrade analysis: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def cleanup_old_trial_events(days_old=90):
    """
    Task mensuelle : Nettoie vieux events trial
    
    Args:
        days_old (int): Age en jours pour suppression
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from .models import TrialEvent
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        deleted_count = TrialEvent.objects.filter(
            created_at__lt=cutoff_date,
            processed=True
        ).delete()[0]
        
        logger.info(f"Trial events nettoyés: {deleted_count} events > {days_old} jours")
        
        return {
            'success': True,
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Erreur cleanup trial events: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }