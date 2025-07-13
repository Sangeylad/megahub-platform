# backend/glossary/models/__init__.py
from .category_models import TermCategory
from .term_models import Term, TermTranslation, TermRelation

__all__ = [
    'TermCategory',
    'Term', 
    'TermTranslation',
    'TermRelation'
]