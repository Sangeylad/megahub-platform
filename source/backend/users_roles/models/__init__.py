# backend/users_roles/models/__init__.py
from .roles import Role, UserRole, Permission, RolePermission

__all__ = ['Role', 'UserRole', 'Permission', 'RolePermission']
