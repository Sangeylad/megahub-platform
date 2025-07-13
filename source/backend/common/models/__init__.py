# backend/common/models/__init__.py

from .mixins import (
    TimestampedMixin,
    SoftDeleteMixin,
    BrandScopedMixin,
    SlugMixin
)

__all__ = [
    'TimestampedMixin',
    'SoftDeleteMixin', 
    'BrandScopedMixin',
    'SlugMixin'
]