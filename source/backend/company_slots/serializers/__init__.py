# backend/company_slots/serializers/__init__.py
from .slots_serializers import (
    CompanySlotsSerializer, CompanySlotsUpdateSerializer, 
    CompanySlotsStatsSerializer
)

__all__ = [
    'CompanySlotsSerializer', 'CompanySlotsUpdateSerializer',
    'CompanySlotsStatsSerializer'
]
