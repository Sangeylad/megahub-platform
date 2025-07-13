# backend/ai_templates_core/filters/template_filters.py
import django_filters
from django.db import models
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta

from ..models import BaseTemplate, TemplateType

# ===== IMPORTS CROSS-APP SÉCURISÉS =====

# Storage/Versioning
try:
    from ai_templates_storage.models import TemplateVersion, TemplateVariable
    HAS_STORAGE = True
except ImportError:
    HAS_STORAGE = False

# Insights
try:
    from ai_templates_insights.models import TemplateRecommendation, TemplateInsight, OptimizationSuggestion
    INSIGHT_TYPE_CHOICES = [
        ('underused', 'Sous-utilisé'),
        ('performance_drop', 'Baisse performance'),
        ('quality_issue', 'Problème qualité'),
        ('trending_up', 'En hausse'),
        ('optimization_needed', 'Optimisation requise')
    ]
    RECOMMENDATION_TYPE_CHOICES = [
        ('trending', 'Tendance'),
        ('personalized', 'Personnalisé'),
        ('similar_brands', 'Marques similaires'),
        ('performance_based', 'Performance'),
        ('new_release', 'Nouveauté')
    ]
    HAS_INSIGHTS = True
except ImportError:
    INSIGHT_TYPE_CHOICES = []
    RECOMMENDATION_TYPE_CHOICES = []
    HAS_INSIGHTS = False

# Workflow
try:
    from ai_templates_workflow.models import TemplateApproval, TemplateValidationResult
    APPROVAL_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending_review', 'En attente de review'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('published', 'Publié')
    ]
    HAS_WORKFLOW = True
except ImportError:
    APPROVAL_STATUS_CHOICES = []
    HAS_WORKFLOW = False

# SEO Templates
try:
    from seo_websites_ai_templates_content.models import SEOWebsiteTemplate
    SEO_PAGE_TYPE_CHOICES = [
        ('landing', 'Landing Page'),
        ('vitrine', 'Page Vitrine'),
        ('service', 'Page Service'),
        ('produit', 'Page Produit'),
        ('blog', 'Article Blog'),
        ('category', 'Page Catégorie')
    ]
    SEO_INTENT_CHOICES = [
        ('TOFU', 'Top of Funnel'),
        ('MOFU', 'Middle of Funnel'),
        ('BOFU', 'Bottom of Funnel'),
        ('BRAND', 'Brand')
    ]
    HAS_SEO_TEMPLATES = True
except ImportError:
    SEO_PAGE_TYPE_CHOICES = []
    SEO_INTENT_CHOICES = []
    HAS_SEO_TEMPLATES = False

class BaseTemplateFilter(django_filters.FilterSet):
    """
    🔥 FILTRE TEMPLATES ULTRA INTELLIGENT
    
    Exemples d'usage :
    GET /templates/?template_type=website&is_active=true&created_after=2024-01-01
    GET /templates/?brand_name=MaBrand&search=landing&workflow_status=approved
    GET /templates/?is_trending=true&has_insights=true&performance_score_min=80
    GET /templates/?created_by_me=true&last_week=true&has_versions=true
    """
    
    # ===== FILTRES DE BASE =====
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    prompt_content = django_filters.CharFilter(lookup_expr='icontains')
    
    # Template Type
    template_type = django_filters.ModelChoiceFilter(queryset=TemplateType.objects.filter(is_active=True))
    template_type_name = django_filters.CharFilter(field_name='template_type__name', lookup_expr='icontains')
    
    # Status
    is_active = django_filters.BooleanFilter()
    is_public = django_filters.BooleanFilter()
    
    # ===== FILTRES BRAND & USER =====
    brand = django_filters.NumberFilter(field_name='brand__id')
    brand_name = django_filters.CharFilter(field_name='brand__name', lookup_expr='icontains')
    company = django_filters.NumberFilter(field_name='brand__company__id')
    company_name = django_filters.CharFilter(field_name='brand__company__name', lookup_expr='icontains')
    
    # Créateur
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    created_by_username = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')
    created_by_me = django_filters.BooleanFilter(method='filter_created_by_me')
    
    # ===== FILTRES TEMPORELS =====
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    # Raccourcis temporels
    last_week = django_filters.BooleanFilter(method='filter_last_week')
    last_month = django_filters.BooleanFilter(method='filter_last_month')
    recent = django_filters.BooleanFilter(method='filter_recent')
    
    # ===== BRAND CONFIG FILTERS =====
    has_brand_config = django_filters.BooleanFilter(method='filter_has_brand_config')
    allows_custom_templates = django_filters.BooleanFilter(field_name='brand__template_config__allow_custom_templates')
    config_style = django_filters.CharFilter(field_name='brand__template_config__default_template_style', lookup_expr='icontains')
    
    # ===== CONTENT ANALYSIS =====
    has_variables = django_filters.BooleanFilter(method='filter_has_variables')
    variable_count = django_filters.RangeFilter(method='filter_variable_count')
    content_length = django_filters.RangeFilter(method='filter_content_length')
    
    # ===== VERSIONING (ai_templates_storage) =====
    has_versions = django_filters.BooleanFilter(method='filter_has_versions')
    version_count = django_filters.RangeFilter(method='filter_version_count')
    current_version = django_filters.NumberFilter(method='filter_current_version')
    has_changelog = django_filters.BooleanFilter(method='filter_has_changelog')
    
    # ===== INSIGHTS (ai_templates_insights) =====
    has_recommendations = django_filters.BooleanFilter(method='filter_has_recommendations')
    recommendation_type = django_filters.ChoiceFilter(
        field_name='template_recommendations__recommendation_type',
        choices=RECOMMENDATION_TYPE_CHOICES
    ) if HAS_INSIGHTS else None
    
    confidence_score_min = django_filters.NumberFilter(
        field_name='template_recommendations__confidence_score',
        lookup_expr='gte'
    ) if HAS_INSIGHTS else None
    
    has_insights = django_filters.BooleanFilter(method='filter_has_insights')
    insight_type = django_filters.ChoiceFilter(
        field_name='insights__insight_type',
        choices=INSIGHT_TYPE_CHOICES
    ) if HAS_INSIGHTS else None
    
    insight_severity = django_filters.ChoiceFilter(
        field_name='insights__severity',
        choices=[('low', 'Faible'), ('medium', 'Moyenne'), ('high', 'Élevée'), ('critical', 'Critique')]
    ) if HAS_INSIGHTS else None
    
    unresolved_insights = django_filters.BooleanFilter(method='filter_unresolved_insights')
    
    # Performance insights
    is_trending = django_filters.BooleanFilter(method='filter_is_trending')
    is_underused = django_filters.BooleanFilter(method='filter_is_underused')
    needs_optimization = django_filters.BooleanFilter(method='filter_needs_optimization')
    
    # ===== WORKFLOW (ai_templates_workflow) =====
    workflow_status = django_filters.ChoiceFilter(
        field_name='approvals__status',
        choices=APPROVAL_STATUS_CHOICES
    ) if HAS_WORKFLOW else None
    
    is_approved = django_filters.BooleanFilter(method='filter_is_approved')
    is_pending_review = django_filters.BooleanFilter(method='filter_is_pending_review')
    needs_approval = django_filters.BooleanFilter(method='filter_needs_approval')
    
    reviewed_by = django_filters.NumberFilter(field_name='approvals__reviewed_by__id')
    submitted_by = django_filters.NumberFilter(field_name='approvals__submitted_by__id')
    reviewed_after = django_filters.DateTimeFilter(field_name='approvals__reviewed_at', lookup_expr='gte')
    
    # Validation
    validation_status = django_filters.ChoiceFilter(method='filter_validation_status')
    has_validation_errors = django_filters.BooleanFilter(method='filter_has_validation_errors')
    
    # ===== SEO TEMPLATES (seo_websites_ai_templates_content) =====
    has_seo_config = django_filters.BooleanFilter(method='filter_has_seo_config')
    seo_page_type = django_filters.ChoiceFilter(
        field_name='seo_config__page_type',
        choices=SEO_PAGE_TYPE_CHOICES
    ) if HAS_SEO_TEMPLATES else None
    
    search_intent = django_filters.ChoiceFilter(
        field_name='seo_config__search_intent',
        choices=SEO_INTENT_CHOICES
    ) if HAS_SEO_TEMPLATES else None
    
    target_word_count = django_filters.RangeFilter(field_name='seo_config__target_word_count')
    
    # ===== PERFORMANCE & ANALYTICS =====
    usage_count = django_filters.RangeFilter(method='filter_usage_count')
    performance_score = django_filters.RangeFilter(method='filter_performance_score')
    is_popular = django_filters.BooleanFilter(method='filter_is_popular')
    recently_used = django_filters.BooleanFilter(method='filter_recently_used')
    
    # ===== RECHERCHE GLOBALE =====
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = BaseTemplate
        fields = [
            'template_type', 'is_active', 'is_public', 'brand', 'created_by'
        ]

    # ===== MÉTHODES DE FILTRAGE =====
    
    # === USER & TEMPORAL METHODS ===
    
    def filter_created_by_me(self, queryset, name, value):
        """Templates créés par l'utilisateur courant"""
        if value and hasattr(self.request, 'user'):
            return queryset.filter(created_by=self.request.user)
        return queryset
    
    def filter_last_week(self, queryset, name, value):
        """Templates créés la semaine dernière"""
        if value:
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        return queryset
    
    def filter_last_month(self, queryset, name, value):
        """Templates créés le mois dernier"""
        if value:
            month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)
        return queryset
    
    def filter_recent(self, queryset, name, value):
        """Templates récents (3 derniers jours)"""
        if value:
            recent_date = timezone.now() - timedelta(days=3)
            return queryset.filter(updated_at__gte=recent_date)
        return queryset
    
    # === BRAND CONFIG METHODS ===
    
    def filter_has_brand_config(self, queryset, name, value):
        """Templates de brands avec/sans config spécifique"""
        if value:
            return queryset.filter(brand__template_config__isnull=False)
        return queryset.filter(brand__template_config__isnull=True)
    
    # === CONTENT ANALYSIS METHODS ===
    
    def filter_has_variables(self, queryset, name, value):
        """Templates utilisant des variables {{var}}"""
        if value:
            return queryset.filter(prompt_content__icontains='{{')
        return queryset.exclude(prompt_content__icontains='{{')
    
    def filter_variable_count(self, queryset, name, value):
        """Estimation du nombre de variables"""
        # Annotation pour compter les variables approximativement
        queryset = queryset.extra(
            select={
                'estimated_variables': "LENGTH(prompt_content) - LENGTH(REPLACE(prompt_content, '{{', ''))"
            }
        )
        
        if value.start is not None:
            queryset = queryset.extra(where=["estimated_variables >= %s"], params=[value.start])
        if value.stop is not None:
            queryset = queryset.extra(where=["estimated_variables <= %s"], params=[value.stop])
        
        return queryset
    
    def filter_content_length(self, queryset, name, value):
        """Longueur du contenu prompt"""
        queryset = queryset.annotate(content_length=models.functions.Length('prompt_content'))
        
        if value.start is not None:
            queryset = queryset.filter(content_length__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(content_length__lte=value.stop)
        
        return queryset
    
    # === VERSIONING METHODS ===
    
    def filter_has_versions(self, queryset, name, value):
        """Templates avec/sans historique de versions"""
        if not HAS_STORAGE:
            return queryset
        if value:
            return queryset.filter(versions__isnull=False).distinct()
        return queryset.filter(versions__isnull=True)
    
    def filter_version_count(self, queryset, name, value):
        """Nombre de versions par template"""
        if not HAS_STORAGE:
            return queryset
        
        queryset = queryset.annotate(version_count=Count('versions', distinct=True))
        
        if value.start is not None:
            queryset = queryset.filter(version_count__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(version_count__lte=value.stop)
        
        return queryset
    
    def filter_current_version(self, queryset, name, value):
        """Templates avec version courante spécifique"""
        if not HAS_STORAGE:
            return queryset
        return queryset.filter(versions__version_number=value, versions__is_current=True)
    
    def filter_has_changelog(self, queryset, name, value):
        """Templates avec/sans changelog détaillé"""
        if not HAS_STORAGE:
            return queryset
        if value:
            return queryset.filter(
                versions__changelog__isnull=False
            ).exclude(versions__changelog='').distinct()
        return queryset.filter(
            Q(versions__changelog__isnull=True) | Q(versions__changelog='')
        ).distinct()
    
    # === INSIGHTS METHODS ===
    
    def filter_has_recommendations(self, queryset, name, value):
        """Templates avec/sans recommandations"""
        if not HAS_INSIGHTS:
            return queryset
        if value:
            return queryset.filter(template_recommendations__isnull=False).distinct()
        return queryset.filter(template_recommendations__isnull=True)
    
    def filter_has_insights(self, queryset, name, value):
        """Templates avec/sans insights automatiques"""
        if not HAS_INSIGHTS:
            return queryset
        if value:
            return queryset.filter(insights__isnull=False).distinct()
        return queryset.filter(insights__isnull=True)
    
    def filter_unresolved_insights(self, queryset, name, value):
        """Templates avec insights non résolus"""
        if not HAS_INSIGHTS:
            return queryset
        if value:
            return queryset.filter(insights__is_resolved=False).distinct()
        return queryset.exclude(insights__is_resolved=False)
    
    def filter_is_trending(self, queryset, name, value):
        """Templates en tendance (insight automatique)"""
        if not HAS_INSIGHTS:
            # Fallback : activité récente
            if value:
                recent_date = timezone.now() - timedelta(days=7)
                return queryset.filter(updated_at__gte=recent_date)
            return queryset
        
        if value:
            return queryset.filter(insights__insight_type='trending_up').distinct()
        return queryset.exclude(insights__insight_type='trending_up')
    
    def filter_is_underused(self, queryset, name, value):
        """Templates sous-utilisés"""
        if not HAS_INSIGHTS:
            return queryset
        if value:
            return queryset.filter(insights__insight_type='underused').distinct()
        return queryset.exclude(insights__insight_type='underused')
    
    def filter_needs_optimization(self, queryset, name, value):
        """Templates nécessitant optimisation"""
        if not HAS_INSIGHTS:
            return queryset
        if value:
            return queryset.filter(insights__insight_type='optimization_needed').distinct()
        return queryset.exclude(insights__insight_type='optimization_needed')
    
    # === WORKFLOW METHODS ===
    
    def filter_is_approved(self, queryset, name, value):
        """Templates approuvés"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(approvals__status='approved').distinct()
        return queryset.exclude(approvals__status='approved')
    
    def filter_is_pending_review(self, queryset, name, value):
        """Templates en attente de review"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(approvals__status='pending_review').distinct()
        return queryset.exclude(approvals__status='pending_review')
    
    def filter_needs_approval(self, queryset, name, value):
        """Templates nécessitant approbation"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(
                Q(approvals__isnull=True) | Q(approvals__status='draft')
            ).distinct()
        return queryset.exclude(
            Q(approvals__isnull=True) | Q(approvals__status='draft')
        )
    
    def filter_validation_status(self, queryset, name, value):
        """Status de validation (passed/failed/pending)"""
        if not HAS_WORKFLOW:
            return queryset
        
        if value == 'passed':
            return queryset.filter(validation_results__is_valid=True).distinct()
        elif value == 'failed':
            return queryset.filter(validation_results__is_valid=False).distinct()
        elif value == 'pending':
            return queryset.filter(validation_results__isnull=True)
        
        return queryset
    
    def filter_has_validation_errors(self, queryset, name, value):
        """Templates avec erreurs de validation"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(validation_results__is_valid=False).distinct()
        return queryset.exclude(validation_results__is_valid=False)
    
    # === SEO METHODS ===
    
    def filter_has_seo_config(self, queryset, name, value):
        """Templates avec configuration SEO"""
        if not HAS_SEO_TEMPLATES:
            return queryset
        if value:
            return queryset.filter(seo_config__isnull=False)
        return queryset.filter(seo_config__isnull=True)
    
    # === PERFORMANCE METHODS ===
    
    def filter_usage_count(self, queryset, name, value):
        """Nombre d'utilisations estimé (placeholder)"""
        # À connecter avec système de tracking réel
        return queryset
    
    def filter_performance_score(self, queryset, name, value):
        """Score de performance calculé (placeholder)"""
        # À connecter avec métriques business réelles
        return queryset
    
    def filter_is_popular(self, queryset, name, value):
        """Templates populaires (fallback: publics)"""
        if value:
            return queryset.filter(is_public=True)
        return queryset
    
    def filter_recently_used(self, queryset, name, value):
        """Templates utilisés récemment (fallback: modifiés)"""
        if value:
            recent_date = timezone.now() - timedelta(days=7)
            return queryset.filter(updated_at__gte=recent_date)
        return queryset
    
    # === RECHERCHE GLOBALE ===
    
    def filter_search(self, queryset, name, value):
        """Recherche globale dans nom, description, contenu"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(prompt_content__icontains=value) |
            Q(template_type__display_name__icontains=value) |
            Q(created_by__username__icontains=value)
        )