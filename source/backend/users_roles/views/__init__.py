# backend/users_roles/views/__init__.py
from .roles_views import RoleViewSet, PermissionViewSet, UserRoleViewSet

__all__ = ['RoleViewSet', 'PermissionViewSet', 'UserRoleViewSet']
