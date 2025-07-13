# backend/seo_keywords_cocoons/serializers/__init__.py

from .cocoon_serializers import (
    CocoonCategorySerializer,
    SemanticCocoonListSerializer,
    SemanticCocoonSerializer,
    SemanticCocoonDetailSerializer  # 🔥 AJOUTÉ
)
from .association_serializers import (
    CocoonKeywordSerializer,
    CocoonKeywordListSerializer
)

__all__ = [
    # Cocoon serializers
    'CocoonCategorySerializer',
    'SemanticCocoonListSerializer', 
    'SemanticCocoonSerializer',
    'SemanticCocoonDetailSerializer',  # 🔥 AJOUTÉ
    
    # Association serializers
    'CocoonKeywordSerializer',
    'CocoonKeywordListSerializer'
]