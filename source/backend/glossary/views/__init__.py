# backend/glossary/views/__init__.py
from .category_views import TermCategoryViewSet
from .term_views import TermViewSet

__all__ = [
    'TermCategoryViewSet',
    'TermViewSet'
]