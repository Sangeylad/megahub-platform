# backend/onboarding_business/services/onboarding.py

from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

from .business_creation import create_solo_business_for_user
from .features_setup import setup_default_features, get_company_features_summary
from .slots_setup import setup_default_slots, get_slots_usage_summary
from .trial_setup import setup_trial_subscription, get_trial_summary
from .roles_setup import assign_default_roles, get_user_roles_summary
from ..exceptions import UserNotEligibleError, BusinessAlreadyExistsError

User = get_user_model()
logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Service principal d'onboarding - Option A
    Remplace les signaux automatiques par setup explicite
    """
    
    @staticmethod
    def is_user_eligible_for_business(user):
        """
        Vérifie si un user est éligible pour création business
        
        Args:
            user (CustomUser): User à vérifier
            
        Returns:
            bool: True si éligible
        """
        # User doit être authentifié et actif
        if not user.is_authenticated or not user.is_active:
            return False
            
        # User ne doit pas avoir de company
        if hasattr(user, 'company') and user.company is not None:
            return False
            
        # User doit avoir email valide
        if not user.email or '@' not in user.email:
            return False
            
        return True
    
    @staticmethod
    def setup_business_for_user(user, business_name=None):
        """
        Setup complet d'un business pour un user - Point d'entrée principal
        
        Args:
            user (CustomUser): User pour qui créer le business
            business_name (str, optional): Nom du business
            
        Returns:
            dict: Résultat complet du setup
            
        Raises:
            UserNotEligibleError: Si user non éligible
            BusinessAlreadyExistsError: Si business existe déjà
        """
        # Vérifications préliminaires
        if not OnboardingService.is_user_eligible_for_business(user):
            raise UserNotEligibleError(user, "User non éligible pour création business")
            
        if hasattr(user, 'company') and user.company is not None:
            raise BusinessAlreadyExistsError(user)
        
        try:
            with transaction.atomic():
                logger.info(f"Début setup business pour {user.username}")
                
                # 1. Création business principal (Company + Brand + User assignment)
                business_result = create_solo_business_for_user(user, business_name)
                company = business_result['company']
                brand = business_result['brand']
                
                logger.info(f"Business principal créé: {company.name}")
                
                # 2. Setup des slots par défaut
                slots = setup_default_slots(company)
                logger.info(f"Slots configurés: {slots.users_slots} users, {slots.brands_slots} brands")
                
                # 3. Setup des features par défaut 
                features = setup_default_features(company)
                logger.info(f"Features activées: {len(features)} features")
                
                # 4. Setup trial subscription
                subscription = setup_trial_subscription(company)
                logger.info(f"Trial subscription: {subscription.status if subscription else 'Non disponible'}")
                
                # 5. Assignment des rôles par défaut
                roles = assign_default_roles(user, company, brand)
                logger.info(f"Rôles assignés: {len(roles)} rôles")
                
                # 6. Compilation du résultat complet
                result = {
                    'company': company,
                    'brand': brand,
                    'slots': slots,
                    'features': features,
                    'subscription': subscription,
                    'roles': roles,
                    'slots_summary': get_slots_usage_summary(company),
                    'features_summary': get_company_features_summary(company),
                    'trial_summary': get_trial_summary(company),
                    'user_roles_summary': get_user_roles_summary(user)
                }
                
                logger.info(f"Setup business terminé avec succès pour {user.username}")
                return result
                
        except Exception as e:
            logger.error(f"Erreur setup business pour {user.username}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod 
    def get_user_business_status(user):
        """
        Status complet du business pour un user
        
        Args:
            user (CustomUser): User à analyser
            
        Returns:
            dict: Status complet
        """
        return {
            'user_id': user.id,
            'username': user.username,
            'is_eligible_for_business': OnboardingService.is_user_eligible_for_business(user),
            'has_business': hasattr(user, 'company') and user.company is not None,
            'onboarding_complete': hasattr(user, 'company') and user.company is not None,
            'business_summary': OnboardingService._get_business_summary(user) if hasattr(user, 'company') and user.company else None
        }
    
    # ✅ FIX : Ajouter la méthode manquante
    @staticmethod
    def get_user_onboarding_status(user):
        """
        Status complet d'onboarding pour un user - Alias pour get_user_business_status
        
        Args:
            user (CustomUser): User à analyser
            
        Returns:
            dict: Status complet d'onboarding
        """
        return OnboardingService.get_user_business_status(user)
    
    @staticmethod
    def _get_business_summary(user):
        """
        Résumé du business pour un user
        
        Args:
            user (CustomUser): User avec business
            
        Returns:
            dict: Résumé business
        """
        if not hasattr(user, 'company') or not user.company:
            return None
            
        company = user.company
        
        return {
            'company_id': company.id,
            'company_name': company.name,
            'business_mode': company.get_business_mode(),
            'is_trial': company.is_in_trial(),
            'trial_days_remaining': company.trial_days_remaining(),
            'brands_count': company.brands.filter(is_deleted=False).count(),
            'users_count': company.members.filter(is_active=True).count(),
            'permissions': user.get_permissions_summary()
        }
    
    @staticmethod
    def extend_trial_period(company, additional_weeks=1):
        """
        Étend la période de trial d'une company
        
        Args:
            company (Company): Company à étendre
            additional_weeks (int): Semaines supplémentaires
            
        Returns:
            bool: True si extension réussie
        """
        if not company.is_in_trial():
            logger.warning(f"Company {company.name} pas en trial - extension impossible")
            return False
        
        # Étendre trial
        old_trial_end = company.trial_expires_at
        company.trial_expires_at = old_trial_end + timedelta(weeks=additional_weeks)
        company.save(update_fields=['trial_expires_at'])
        
        # Étendre features si nécessaire
        company.company_features.filter(
            expires_at=old_trial_end
        ).update(expires_at=company.trial_expires_at)
        
        logger.info(f"Trial étendu pour {company.name}: +{additional_weeks} semaines")
        return True