# backend/seo_pages_workflow/filters/workflow_filters.py

import django_filters
from django.db import models
from django.utils import timezone

from ..models import PageStatus, PageWorkflowHistory, PageScheduling

class PageStatusFilter(django_filters.FilterSet):
    """Filtres pour statuts workflow des pages"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    status = django_filters.ChoiceFilter(choices=PageStatus.PAGE_STATUS_CHOICES)
    status_changed_by = django_filters.NumberFilter()
    
    # Filtres par dates
    status_changed_after = django_filters.DateTimeFilter(
        field_name='status_changed_at', 
        lookup_expr='gte'
    )
    status_changed_before = django_filters.DateTimeFilter(
        field_name='status_changed_at', 
        lookup_expr='lte'
    )
    
    # Filtres par statut groupés
    is_in_production = django_filters.BooleanFilter(method='filter_is_in_production')
    is_published = django_filters.BooleanFilter(method='filter_is_published')
    can_be_published = django_filters.BooleanFilter(method='filter_can_be_published')
    needs_review = django_filters.BooleanFilter(method='filter_needs_review')
    
    # Recherche
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PageStatus
        fields = ['page', 'status', 'status_changed_by']
    
    def filter_is_in_production(self, queryset, name, value):
        """Filtre pages en cours de production"""
        production_statuses = ['draft', 'in_progress', 'pending_review', 'under_review', 'changes_requested', 'approved']
        if value:
            return queryset.filter(status__in=production_statuses)
        else:
            return queryset.exclude(status__in=production_statuses)
    
    def filter_is_published(self, queryset, name, value):
        """Filtre pages publiées"""
        if value:
            return queryset.filter(status='published')
        else:
            return queryset.exclude(status='published')
    
    def filter_can_be_published(self, queryset, name, value):
        """Filtre pages prêtes à être publiées"""
        publishable_statuses = ['approved', 'scheduled']
        if value:
            return queryset.filter(status__in=publishable_statuses)
        else:
            return queryset.exclude(status__in=publishable_statuses)
    
    def filter_needs_review(self, queryset, name, value):
        """Filtre pages nécessitant une review"""
        review_statuses = ['pending_review', 'under_review', 'changes_requested']
        if value:
            return queryset.filter(status__in=review_statuses)
        else:
            return queryset.exclude(status__in=review_statuses)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans titre de page et notes"""
        return queryset.filter(
            models.Q(page__title__icontains=value) |
            models.Q(production_notes__icontains=value)
        )

class PageWorkflowHistoryFilter(django_filters.FilterSet):
    """Filtres pour historique workflow"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    old_status = django_filters.ChoiceFilter(choices=PageStatus.PAGE_STATUS_CHOICES)
    new_status = django_filters.ChoiceFilter(choices=PageStatus.PAGE_STATUS_CHOICES)
    changed_by = django_filters.NumberFilter()
    
    # Filtres par dates
    changed_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    changed_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    today = django_filters.BooleanFilter(method='filter_today')
    
    # Filtres par type de transition
    status_progression = django_filters.BooleanFilter(method='filter_status_progression')
    status_regression = django_filters.BooleanFilter(method='filter_status_regression')
    
    class Meta:
        model = PageWorkflowHistory
        fields = ['page', 'old_status', 'new_status', 'changed_by']
    
    def filter_today(self, queryset, name, value):
        """Filtre changements d'aujourd'hui"""
        if value:
            today = timezone.now().date()
            return queryset.filter(created_at__date=today)
        return queryset
    
    def filter_status_progression(self, queryset, name, value):
        """Filtre progressions de statut (vers published)"""
        progressions = [
            ('draft', 'in_progress'),
            ('in_progress', 'pending_review'),
            ('pending_review', 'approved'),
            ('approved', 'published')
        ]
        
        if value:
            filters = models.Q()
            for old, new in progressions:
                filters |= models.Q(old_status=old, new_status=new)
            return queryset.filter(filters)
        return queryset
    
    def filter_status_regression(self, queryset, name, value):
        """Filtre régressions de statut (retours en arrière)"""
        regressions = [
            ('published', 'archived'),
            ('approved', 'changes_requested'),
            ('under_review', 'changes_requested')
        ]
        
        if value:
            filters = models.Q()
            for old, new in regressions:
                filters |= models.Q(old_status=old, new_status=new)
            return queryset.filter(filters)
        return queryset

class PageSchedulingFilter(django_filters.FilterSet):
    """Filtres pour programmation publication"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    auto_publish = django_filters.BooleanFilter()
    
    # Filtres par dates de programmation
    scheduled_after = django_filters.DateTimeFilter(
        field_name='scheduled_publish_date', 
        lookup_expr='gte'
    )
    scheduled_before = django_filters.DateTimeFilter(
        field_name='scheduled_publish_date', 
        lookup_expr='lte'
    )
    scheduled_today = django_filters.BooleanFilter(method='filter_scheduled_today')
    
    # Filtres par état
    is_ready_to_publish = django_filters.BooleanFilter(method='filter_is_ready_to_publish')
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    
    class Meta:
        model = PageScheduling
        fields = ['page', 'auto_publish']
    
    def filter_scheduled_today(self, queryset, name, value):
        """Filtre programmations d'aujourd'hui"""
        if value:
            today = timezone.now().date()
            return queryset.filter(scheduled_publish_date__date=today)
        return queryset
    
    def filter_is_ready_to_publish(self, queryset, name, value):
        """Filtre pages prêtes à publier maintenant"""
        now = timezone.now()
        if value:
            return queryset.filter(scheduled_publish_date__lte=now)
        else:
            return queryset.filter(scheduled_publish_date__gt=now)
    
    def filter_is_overdue(self, queryset, name, value):
        """Filtre programmations en retard"""
        now = timezone.now()
        if value:
            return queryset.filter(
                scheduled_publish_date__lt=now,
                page__workflow_status__status='scheduled'
            )
        return queryset
