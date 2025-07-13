# backend/seo_websites_core/views/__init__.py

from .website_views import WebsiteViewSet  # ✅ FIX: website_views pas website_models

__all__ = ['WebsiteViewSet']