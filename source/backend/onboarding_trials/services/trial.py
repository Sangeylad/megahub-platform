# backend/onboarding_trials/services/trial.py
from django.utils import timezone
from datetime import timedelta
import logging

from ..models import TrialEvent

logger = logging.getLogger(__name__)

def create_trial_event(company, event_type, event_data=None, triggered_by=None):
    """
    Crée un événement trial
    
    Args:
        company (Company): Company concernée
        event_type (str): Type d'événement
        event_data (dict): Données supplémentaires
        triggered_by (CustomUser): User déclencheur
        
    Returns:
        TrialEvent: Événement créé
    """
    event = TrialEvent.objects.create(
        company=company,
        event_type=event_type,
        event_data=event_data or {},
        triggered_by=triggered_by
    )
    
    logger.info(f"Trial event créé: {event_type} pour {company.name}")
    return event

def start_trial_tracking(company):
    """
    Démarre le tracking trial pour une company
    
    Args:
        company (Company): Company en trial
    """
    if not company.is_in_trial():
        logger.warning(f"Company {company.name} pas en trial - skip tracking")
        return
    
    # Event trial start
    create_trial_event(
        company=company,
        event_type='trial_start',
        event_data={
            'trial_expires_at': company.trial_expires_at.isoformat(),
            'trial_duration_weeks': 2
        }
    )

def check_trial_warnings():
    """
    Vérifie et envoie les avertissements trial
    Task périodique (daily)
    
    Returns:
        int: Nombre d'avertissements envoyés
    """
    now = timezone.now()
    warnings_sent = 0
    
    # Warning thresholds
    warning_thresholds = [
        (7, 'trial_warning_7'),
        (3, 'trial_warning_3'), 
        (1, 'trial_warning_1')
    ]
    
    for days_before, event_type in warning_thresholds:
        warning_date = now + timedelta(days=days_before)
        
        # Companies à avertir
        companies_to_warn = Company.objects.filter(
            is_active=True,
            trial_expires_at__date=warning_date.date(),
            trial_expires_at__gt=now
        ).exclude(
            trial_events__event_type=event_type
        )
        
        for company in companies_to_warn:
            create_trial_event(
                company=company,
                event_type=event_type,
                event_data={
                    'days_remaining': days_before,
                    'trial_expires_at': company.trial_expires_at.isoformat()
                }
            )
            
            # Envoyer notification
            send_trial_warning_notification(company, days_before)
            warnings_sent += 1
    
    logger.info(f"Trial warnings envoyés: {warnings_sent}")
    return warnings_sent

def check_expired_trials():
    """
    Vérifie les trials expirés
    Task périodique (daily)
    
    Returns:
        int: Nombre de trials expirés traités
    """
    now = timezone.now()
    expired_count = 0
    
    # Companies avec trial expiré
    expired_companies = Company.objects.filter(
        is_active=True,
        trial_expires_at__lt=now
    ).exclude(
        trial_events__event_type='trial_expired'
    )
    
    for company in expired_companies:
        create_trial_event(
            company=company,
            event_type='trial_expired',
            event_data={
                'expired_at': now.isoformat(),
                'was_trial_duration_days': (now - (company.trial_expires_at - timedelta(weeks=2))).days
            }
        )
        
        # Logique expiration trial
        handle_trial_expiration(company)
        expired_count += 1
    
    logger.info(f"Trials expirés traités: {expired_count}")
    return expired_count

def extend_trial(company, additional_weeks=1, triggered_by=None):
    """
    Étend un trial
    
    Args:
        company (Company): Company à étendre
        additional_weeks (int): Semaines supplémentaires
        triggered_by (CustomUser): User qui étend
        
    Returns:
        bool: True si extension réussie
    """
    if not company.is_in_trial():
        logger.warning(f"Company {company.name} pas en trial - extension impossible")
        return False
    
    # Étendre trial
    old_expires_at = company.trial_expires_at
    company.trial_expires_at = old_expires_at + timedelta(weeks=additional_weeks)
    company.save(update_fields=['trial_expires_at'])
    
    # Event extension
    create_trial_event(
        company=company,
        event_type='trial_extended',
        event_data={
            'old_expires_at': old_expires_at.isoformat(),
            'new_expires_at': company.trial_expires_at.isoformat(),
            'additional_weeks': additional_weeks
        },
        triggered_by=triggered_by
    )
    
    # Étendre subscription et features
    from onboarding_business.services.trial_setup import extend_trial_period
    extend_trial_period(company, additional_weeks)
    
    logger.info(f"Trial étendu pour {company.name}: +{additional_weeks} semaines")
    return True

def get_trial_analytics(company):
    """
    Analytics trial pour une company
    
    Args:
        company (Company): Company à analyser
        
    Returns:
        dict: Analytics trial
    """
    events = company.trial_events.order_by('created_at')
    
    return {
        'is_trial': company.is_in_trial(),
        'trial_expires_at': company.trial_expires_at,
        'days_remaining': company.trial_days_remaining(),
        'events_count': events.count(),
        'events': [event.get_event_summary() for event in events],
        'last_event': events.last().get_event_summary() if events.exists() else None
    }

def send_trial_warning_notification(company, days_remaining):
    """
    Envoie notification trial warning
    
    Args:
        company (Company): Company à notifier
        days_remaining (int): Jours restants
    """
    # TODO: Intégrer avec système notifications
    logger.info(f"Trial warning notification: {company.name} - {days_remaining} jours restants")

def handle_trial_expiration(company):
    """
    Gère l'expiration d'un trial
    
    Args:
        company (Company): Company expirée
    """
    # TODO: Logique expiration trial
    # - Désactiver features premium
    # - Envoyer notification
    # - Proposer upgrade
    logger.info(f"Trial expiré géré pour {company.name}")