# backend/onboarding_business/permissions.py

from rest_framework import permissions
from common.permissions.business_permissions import IsAuthenticated


class CanSetupBusiness(permissions.BasePermission):
    """Permission pour setup business - User sans company existante"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # User ne doit pas avoir de company
        return not hasattr(request.user, 'company') or request.user.company is None


class CanExtendTrial(permissions.BasePermission):
    """Permission pour étendre trial - Company admin uniquement"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Must have company and be admin
        if not hasattr(request.user, 'company') or not request.user.company:
            return False
            
        return request.user.is_company_admin()


class CanViewBusinessStats(permissions.BasePermission):
    """Permission pour voir stats business - Membres company"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Must have company
        return hasattr(request.user, 'company') and request.user.company is not None