# backend/common/permissions/__init__.py
# Base classes
from .base_permissions import *
from .mixins import *

# Business permissions  
from .business_permissions import *

__all__ = [
    # Base Classes
    'BaseResourcePermission',
    'HeaderBasedScopePermission', 
    'AdminPermission',
    'OwnershipPermission',
    'ReadOnlyOrAuthenticatedPermission',
    'ModelBasedPermission',
    
    # Mixins
    'AdminBypassMixin',
    'ScopeValidationMixin', 
    'CacheablePermissionMixin',
    'AuditPermissionMixin',
    
    # Business Permissions
    'IsCompanyAdmin',
    'IsBrandAdmin', 
    'IsBrandMember',
    'IsBrandOwner',
    'IsWebsiteMember',
    'IsAuthorOrAdmin',
    'IsBlogAuthor',
    'ReadOnlyOrBrandMember',
    'DynamicBrandPermission',
    
    # Aliases (compatibilité)
    'IsBrandMemberPermission',
    'IsCompanyAdminPermission',
    'IsBrandAdminPermission',
]