# /var/www/megahub/backend/crm_entities_core/models/__init__.py

from .base_models import CRMBaseMixin, GDPRMixin
from .account_models import Account
from .contact_models import Contact
from .opportunity_models import Opportunity

__all__ = [
    'CRMBaseMixin',
    'GDPRMixin',
    'Account',
    'Contact',
    'Opportunity'
]
