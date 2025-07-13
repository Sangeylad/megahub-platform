# backend/seo_keywords_ppa/serializers/__init__.py

from .ppa_serializers import (
    PPASerializer, 
    PPAListSerializer, 
    KeywordPPASerializer,
    KeywordPPAListSerializer  # ✅ Ajouter cette ligne manquante
)

__all__ = [
    'PPASerializer', 
    'PPAListSerializer', 
    'KeywordPPASerializer',
    'KeywordPPAListSerializer'  # ✅ Ajouter cette ligne manquante aussi
]