# backend/onboarding_business/services/__init__.py

from .onboarding import OnboardingService
from .business_creation import (
    create_solo_business_for_user, 
    get_business_creation_summary
)
from .features_setup import (
    setup_default_features,
    get_company_features_summary
)
from .slots_setup import (
    setup_default_slots,
    get_slots_usage_summary
)
from .trial_setup import (
    setup_trial_subscription,
    get_trial_summary
)
from .roles_setup import (
    assign_default_roles,
    get_user_roles_summary
)

__all__ = [
    'OnboardingService',
    'create_solo_business_for_user',
    'get_business_creation_summary',
    'setup_default_features',
    'get_company_features_summary',
    'setup_default_slots',
    'get_slots_usage_summary',
    'setup_trial_subscription',
    'get_trial_summary',
    'assign_default_roles',
    'get_user_roles_summary',
]