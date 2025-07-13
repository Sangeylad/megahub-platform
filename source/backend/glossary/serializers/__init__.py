# backend/glossary/serializers/__init__.py
from .category_serializers import TermCategorySerializer, TermCategoryListSerializer, TermCategoryTreeSerializer
from .term_serializers import (
    TermSerializer, 
    TermListSerializer, 
    TermDetailSerializer,
    TermTranslationSerializer,
    TermCreateUpdateSerializer  # ✅ AJOUT
)

__all__ = [
    'TermCategorySerializer',
    'TermCategoryListSerializer', 
    'TermCategoryTreeSerializer',
    'TermSerializer',
    'TermListSerializer',
    'TermDetailSerializer',
    'TermTranslationSerializer',
    'TermCreateUpdateSerializer'  # ✅ AJOUT
]