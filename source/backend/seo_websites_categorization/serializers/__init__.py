# backend/seo_websites_categorization/serializers/__init__.py

from .base_serializers import SeoWebsitesCategorizationBaseSerializer  # ✅ AJOUT
from .category_serializers import (
    WebsiteCategoryListSerializer,
    WebsiteCategoryDetailSerializer,
    WebsiteCategoryCreateSerializer,
    WebsiteCategorizationListSerializer,
    WebsiteCategorizationDetailSerializer,
    WebsiteCategorizationCreateSerializer
)

__all__ = [
    'SeoWebsitesCategorizationBaseSerializer',  # ✅ AJOUT
    'WebsiteCategoryListSerializer',
    'WebsiteCategoryDetailSerializer', 
    'WebsiteCategoryCreateSerializer',
    'WebsiteCategorizationListSerializer',
    'WebsiteCategorizationDetailSerializer',
    'WebsiteCategorizationCreateSerializer'
]