# backend/onboarding_business/exceptions.py

from rest_framework.exceptions import ValidationError, PermissionDenied


class OnboardingError(Exception):
    """Erreur de base pour l'onboarding business"""
    pass


class UserNotEligibleError(OnboardingError):
    """User non éligible pour création business"""
    def __init__(self, user, reason):
        self.user = user
        self.reason = reason
        super().__init__(f"User {user.username} non éligible: {reason}")


class BusinessAlreadyExistsError(OnboardingError):
    """User a déjà un business"""
    def __init__(self, user):
        self.user = user
        super().__init__(f"User {user.username} a déjà un business")


class SlotsLimitReachedError(OnboardingError):
    """Limite de slots atteinte"""
    def __init__(self, company, slot_type):
        self.company = company
        self.slot_type = slot_type
        super().__init__(f"Limite {slot_type} atteinte pour {company.name}")


class TrialExpiredError(OnboardingError):
    """Trial expiré"""
    def __init__(self, company):
        self.company = company
        super().__init__(f"Trial expiré pour {company.name}")


class OnboardingValidationError(ValidationError):
    """Erreur de validation onboarding pour API"""
    pass


class OnboardingPermissionError(PermissionDenied):
    """Erreur de permissions onboarding pour API"""
    pass