# backend/common/serializers/__init__.py

from .mixins import (
    DynamicFieldsSerializer,
    TimestampedSerializer,
    UserOwnedSerializer,
    BrandScopedSerializer,
    WebsiteScopedSerializer,
    SearchableSerializerMixin,
    StatsMixin,
    SlugMixin,
    RelatedFieldsMixin
)

__all__ = [
    'DynamicFieldsSerializer',
    'TimestampedSerializer',
    'UserOwnedSerializer',
    'BrandScopedSerializer',
    'WebsiteScopedSerializer',
    'SearchableSerializerMixin',
    'StatsMixin',
    'SlugMixin',
    'RelatedFieldsMixin'
]