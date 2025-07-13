# backend/file_compressor/permissions/compression_permissions.py
from rest_framework.permissions import BasePermission

class IsBrandMember(BasePermission):
    """Permission pour vérifier l'appartenance à une brand"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Vérifier que l'utilisateur a une brand active
        return hasattr(request.user, 'current_brand') and request.user.current_brand is not None

class CanCompress(BasePermission):
    """Permission pour vérifier si l'utilisateur peut compresser"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'current_brand') or not request.user.current_brand:
            return False
        
        # Vérification des quotas se fait dans la vue
        return True