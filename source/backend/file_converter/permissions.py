# backend/file_converter/permissions.py
from brands_core.permissions.brand_permissions import IsBrandMember as BaseBrandMember

class IsBrandMember(BaseBrandMember):
    """Utilise la permission existante de business"""
    pass

# Ou directement dans les imports des views, on utilisera celle de business