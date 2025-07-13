# backend/blog_content/filters/content_filters.py

import django_filters
from django.db.models import Q
from ..models import BlogArticle, BlogAuthor, BlogTag


class BlogArticleFilter(django_filters.FilterSet):
    """Filtres avancés pour articles blog"""
    
    # Filtres texte
    search = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    # Filtres par relations
    author = django_filters.ModelChoiceFilter(
        field_name='primary_author',
        queryset=BlogAuthor.objects.all(),
        label='Auteur'
    )
    
    tag = django_filters.ModelChoiceFilter(
        field_name='tags',
        queryset=BlogTag.objects.all(),
        label='Tag'
    )
    
    # Filtres par contenu
    has_featured_image = django_filters.BooleanFilter(
        method='filter_has_featured_image',
        label='A une image mise en avant'
    )
    
    # Filtres par métriques
    word_count_min = django_filters.NumberFilter(
        field_name='word_count',
        lookup_expr='gte',
        label='Nombre de mots minimum'
    )
    word_count_max = django_filters.NumberFilter(
        field_name='word_count',
        lookup_expr='lte',
        label='Nombre de mots maximum'
    )
    
    reading_time_min = django_filters.NumberFilter(
        field_name='reading_time_minutes',
        lookup_expr='gte',
        label='Temps de lecture minimum (min)'
    )
    reading_time_max = django_filters.NumberFilter(
        field_name='reading_time_minutes',
        lookup_expr='lte',
        label='Temps de lecture maximum (min)'
    )
    
    # Filtres par Page
    page_type = django_filters.ChoiceFilter(
        field_name='page__page_type',
        choices=[
            ('blog', 'Blog'),
            ('blog_category', 'Catégorie Blog'),
        ],
        label='Type de page'
    )
    
    page_status = django_filters.ChoiceFilter(
        field_name='page__status',
        choices=[
            ('draft', 'Brouillon'),
            ('published', 'Publié'),
            ('archived', 'Archivé'),
        ],
        label='Statut page'
    )
    
    # Filtres par Website
    website = django_filters.NumberFilter(
        field_name='page__website_id',
        label='Site web'
    )
    
    # Filtres par dates
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Créé après'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Créé avant'
    )
    
    class Meta:
        model = BlogArticle
        fields = [
            'search', 'author', 'tag', 'has_featured_image',
            'word_count_min', 'word_count_max',
            'reading_time_min', 'reading_time_max',
            'page_type', 'page_status', 'website',
            'created_after', 'created_before'
        ]
    
    def filter_search(self, queryset, name, value):
        """Recherche textuelle multi-champs"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(page__title__icontains=value) |
            Q(excerpt__icontains=value) |
            Q(focus_keyword__icontains=value) |
            Q(primary_author__display_name__icontains=value)
        )
    
    def filter_has_featured_image(self, queryset, name, value):
        """Filtre par présence image featured"""
        if value is True:
            return queryset.exclude(featured_image_url='')
        elif value is False:
            return queryset.filter(featured_image_url='')
        return queryset


class BlogAuthorFilter(django_filters.FilterSet):
    """Filtres pour auteurs blog"""
    
    search = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    has_articles = django_filters.BooleanFilter(
        method='filter_has_articles',
        label='A des articles'
    )
    
    expertise_topic = django_filters.CharFilter(
        method='filter_expertise',
        label='Expertise'
    )
    
    class Meta:
        model = BlogAuthor
        fields = ['search', 'has_articles', 'expertise_topic']
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        
        return queryset.filter(
            Q(display_name__icontains=value) |
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(bio__icontains=value)
        )
    
    def filter_has_articles(self, queryset, name, value):
        if value is True:
            return queryset.filter(articles_count__gt=0)
        elif value is False:
            return queryset.filter(articles_count=0)
        return queryset
    
    def filter_expertise(self, queryset, name, value):
        if not value:
            return queryset
        
        return queryset.filter(expertise_topics__icontains=value)


class BlogTagFilter(django_filters.FilterSet):
    """Filtres pour tags blog"""
    
    search = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    is_used = django_filters.BooleanFilter(
        method='filter_is_used',
        label='Utilisé'
    )
    
    color = django_filters.CharFilter(
        field_name='color',
        lookup_expr='iexact',
        label='Couleur'
    )
    
    class Meta:
        model = BlogTag
        fields = ['search', 'is_used', 'color']
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_is_used(self, queryset, name, value):
        if value is True:
            return queryset.filter(usage_count__gt=0)
        elif value is False:
            return queryset.filter(usage_count=0)
        return queryset
