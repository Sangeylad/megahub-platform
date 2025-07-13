# backend/ai_core/filters/core_filters.py

import django_filters
from ..models import AIJob, AIJobType

class AIJobFilter(django_filters.FilterSet):
    """Filtres pour jobs IA"""
    status = django_filters.ChoiceFilter(choices=AIJob._meta.get_field('status').choices)
    job_type = django_filters.ModelChoiceFilter(queryset=AIJobType.objects.all())
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_async = django_filters.BooleanFilter()
    priority = django_filters.ChoiceFilter(choices=AIJob._meta.get_field('priority').choices)
    search = django_filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        """Recherche dans job_id, description, job_type"""
        return queryset.filter(
            models.Q(job_id__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(job_type__name__icontains=value)
        )
    
    class Meta:
        model = AIJob
        fields = ['status', 'job_type', 'is_async', 'priority']
