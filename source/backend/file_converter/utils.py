# backend/file_converter/utils.py
from brands_core.models import Brand

def get_user_brands(user):
    """Récupère les brands accessibles pour un utilisateur"""
    if user.is_company_admin():
        return Brand.objects.filter(company=user.company)
    else:
        return user.brands.all()

def get_default_brand_for_user(user):
    """Récupère la première brand accessible pour un utilisateur"""
    brands = get_user_brands(user)
    return brands.first() if brands.exists() else None