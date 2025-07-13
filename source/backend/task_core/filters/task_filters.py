# backend/task_core/filters/task_filters.py

import django_filters
from django.db import models
from ..models import BaseTask

class BaseTaskFilter(django_filters.FilterSet):
    """Filtres pour BaseTask - extensible par autres apps"""
    
    # Filtres de base
    task_type = django_filters.CharFilter(lookup_expr='iexact')
    status = django_filters.ChoiceFilter(choices=BaseTask.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=BaseTask.PRIORITY_CHOICES)
    
    # Recherche textuelle
    search = django_filters.CharFilter(method='filter_search')
    
    # Dates
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Utilisateur
    created_by = django_filters.NumberFilter(field_name='created_by_id')
    
    class Meta:
        model = BaseTask
        fields = ['task_type', 'status', 'priority', 'queue_name']
    
    def filter_search(self, queryset, name, value):
        """Recherche dans description, task_id, task_type"""
        return queryset.filter(
            models.Q(description__icontains=value) |
            models.Q(task_id__icontains=value) |
            models.Q(task_type__icontains=value)
        )
