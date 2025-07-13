# backend/glossary/views/term_views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db.models import Q, F, Count, Case, When, IntegerField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import django_filters

from glossary.models import Term, TermTranslation, TermCategory
from glossary.serializers import (
    TermSerializer,
    TermListSerializer, 
    TermDetailSerializer,
    TermTranslationSerializer,
    TermCreateUpdateSerializer
)
from glossary.throttling import GlossaryReadThrottle, GlossarySearchThrottle, GlossaryStatsThrottle


class TermFilter(django_filters.FilterSet):
    """Filtres avancés pour les termes"""
    
    # ✅ FILTRE HIÉRARCHIQUE : inclut les sous-catégories
    category = django_filters.CharFilter(method='filter_by_category_hierarchy')
    category_slug = django_filters.CharFilter(method='filter_by_category_hierarchy')
    category_id = django_filters.ModelChoiceFilter(
        field_name='category',
        queryset=TermCategory.objects.all()
    )
    
    language = django_filters.CharFilter(method='filter_by_language')
    has_translation = django_filters.CharFilter(method='filter_has_translation')
    difficulty = django_filters.ChoiceFilter(
        field_name='difficulty_level',
        choices=Term._meta.get_field('difficulty_level').choices
    )
    essential = django_filters.BooleanFilter(field_name='is_essential')
    popularity_min = django_filters.NumberFilter(field_name='popularity_score', lookup_expr='gte')
    popularity_max = django_filters.NumberFilter(field_name='popularity_score', lookup_expr='lte')
    
    class Meta:
        model = Term
        fields = ['category', 'category_slug', 'category_id', 'is_essential', 'difficulty_level']
    
    def filter_by_category_hierarchy(self, queryset, name, value):
        """
        ✅ NOUVEAU : Filtre hiérarchique incluant les sous-catégories
        """
        if not value:
            return queryset
            
        try:
            # Trouver la catégorie par slug
            category = TermCategory.objects.get(slug=value)
            
            # Récupérer tous les IDs : catégorie + descendants
            category_ids = [category.id]
            
            # Si la catégorie a des enfants, les inclure
            if hasattr(category, 'get_descendants'):
                descendant_ids = list(category.get_descendants().values_list('id', flat=True))
                category_ids.extend(descendant_ids)
            else:
                # Fallback : chercher manuellement les enfants
                children = TermCategory.objects.filter(parent=category)
                category_ids.extend(children.values_list('id', flat=True))
                
                # Et les petits-enfants
                grandchildren = TermCategory.objects.filter(parent__in=children)
                category_ids.extend(grandchildren.values_list('id', flat=True))
            
            print(f"🔍 Category '{value}' includes IDs: {category_ids}")  # DEBUG
            
            return queryset.filter(category_id__in=category_ids)
            
        except TermCategory.DoesNotExist:
            print(f"❌ Category '{value}' not found")  # DEBUG
            return queryset.none()
    
    def filter_by_language(self, queryset, name, value):
        return queryset.filter(translations__language=value).distinct()
    
    def filter_has_translation(self, queryset, name, value):
        if value.lower() == 'true':
            return queryset.filter(translations__isnull=False).distinct()
        elif value.lower() == 'false':
            return queryset.filter(translations__isnull=True)
        return queryset


class TermViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour les termes du glossaire
    
    Lecture (publique):
    - GET /glossaire/terms/ - Liste avec filtres
    - GET /glossaire/terms/{id}/ - Détail
    - GET /glossaire/terms/by-slug/{slug}/ - Par slug
    - GET /glossaire/terms/search/ - Recherche
    - GET /glossaire/terms/popular/ - Populaires
    - GET /glossaire/terms/essential/ - Essentiels
    
    Écriture (admin/staff seulement):
    - POST /glossaire/terms/ - Créer
    - PUT /glossaire/terms/{id}/ - Modifier
    - PATCH /glossaire/terms/{id}/ - Modifier partiellement
    - DELETE /glossaire/terms/{id}/ - Supprimer
    """
    
    queryset = Term.objects.filter(is_active=True).select_related('category').prefetch_related(
        'translations', 
        'relations_from__to_term__category',
        'relations_to__from_term'
    )
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TermFilter
    search_fields = ['slug', 'translations__title', 'translations__definition']
    ordering_fields = ['popularity_score', 'created_at', 'updated_at', 'slug']
    ordering = ['-popularity_score', 'slug']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]
    
    def get_throttle_classes(self):
        if self.action == 'search':
            return [GlossarySearchThrottle]
        elif self.action == 'stats':
            return [GlossaryStatsThrottle]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return []
        else:
            return [GlossaryReadThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TermListSerializer
        elif self.action in ['retrieve', 'by_slug']:
            return TermDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TermCreateUpdateSerializer
        return TermSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.query_params.get('lang', 'fr')
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ÉCRITURE : Inclure les termes inactifs pour les admins
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Term.objects.all().select_related('category').prefetch_related(
                'translations', 
                'relations_from__to_term__category',
                'relations_to__from_term'
            )
        
        # Filtres existants
        category_path = self.request.query_params.get('category_path')
        related_to = self.request.query_params.get('related_to')
        exclude = self.request.query_params.get('exclude')
        
        if category_path:
            try:
                category = TermCategory.objects.get(slug=category_path.split('/')[-1])
                category_ids = [category.id] + list(
                    category.get_descendants().values_list('id', flat=True)
                )
                queryset = queryset.filter(category_id__in=category_ids)
            except TermCategory.DoesNotExist:
                pass
        
        if related_to:
            try:
                related_term = Term.objects.get(slug=related_to)
                related_ids = related_term.relations_from.values_list('to_term_id', flat=True)
                queryset = queryset.filter(id__in=related_ids)
            except Term.DoesNotExist:
                pass
        
        if exclude:
            exclude_ids = exclude.split(',')
            queryset = queryset.exclude(id__in=exclude_ids)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """CRÉATION avec gestion des traductions"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        term = serializer.save()
        
        detail_serializer = TermDetailSerializer(term, context=self.get_serializer_context())
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """MISE À JOUR avec gestion des traductions"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        term = serializer.save()
        
        detail_serializer = TermDetailSerializer(term, context=self.get_serializer_context())
        return Response(detail_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        language = request.query_params.get('lang', 'fr')
        context = request.query_params.get('context', '')
        
        try:
            term = self.get_queryset().get(slug=slug)
            
            if context:
                translation = term.translations.filter(
                    language=language, 
                    context=context
                ).first()
                if not translation:
                    return Response(
                        {'error': f'Terme non trouvé pour le contexte "{context}"'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Incrémenter popularité
            term.popularity_score = F('popularity_score') + 1
            term.save(update_fields=['popularity_score'])
            term.refresh_from_db()
            
            serializer = self.get_serializer(term)
            return Response(serializer.data)
            
        except Term.DoesNotExist:
            return Response(
                {'error': 'Terme non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        language = request.query_params.get('lang', 'fr')
        category_slug = request.query_params.get('category', '')
        essential = request.query_params.get('essential', '')
        difficulty = request.query_params.get('difficulty', '')
        
        # ✅ CORRECTION : Permettre la recherche par filtres uniquement
        # Plus besoin de paramètre "q" obligatoire
        
        queryset = self.get_queryset()
        
        # ✅ Appliquer le filtre hiérarchique des catégories
        if category_slug:
            try:
                category = TermCategory.objects.get(slug=category_slug)
                category_ids = [category.id]
                
                # Inclure les sous-catégories
                if hasattr(category, 'get_descendants'):
                    descendant_ids = list(category.get_descendants().values_list('id', flat=True))
                    category_ids.extend(descendant_ids)
                else:
                    children = TermCategory.objects.filter(parent=category)
                    category_ids.extend(children.values_list('id', flat=True))
                    grandchildren = TermCategory.objects.filter(parent__in=children)
                    category_ids.extend(grandchildren.values_list('id', flat=True))
                
                queryset = queryset.filter(category_id__in=category_ids)
            except TermCategory.DoesNotExist:
                pass
        
        # ✅ Filtres additionnels
        if essential and essential.lower() == 'true':
            queryset = queryset.filter(is_essential=True)
        
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # ✅ Recherche textuelle seulement si query fournie
        if query:
            queryset = queryset.filter(
                Q(translations__language=language) &
                (
                    Q(translations__title__icontains=query) |
                    Q(translations__definition__icontains=query) |
                    Q(slug__icontains=query)
                )
            ).distinct()
            
            queryset = queryset.annotate(
                relevance_score=Case(
                    When(translations__title__iexact=query, then=3),
                    When(translations__title__icontains=query, then=2),
                    When(translations__definition__icontains=query, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('-relevance_score', '-popularity_score')
        else:
            # ✅ Si pas de query, trier par popularité
            queryset = queryset.order_by('-popularity_score', 'slug')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TermListSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)
        
        serializer = TermListSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().order_by('-popularity_score')[:limit]
        
        serializer = TermListSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def essential(self, request):
        queryset = self.get_queryset().filter(is_essential=True)
        
        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        serializer = TermListSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        term = self.get_object()
        limit = int(request.query_params.get('limit', 5))
        
        related_ids = term.relations_from.values_list('to_term_id', flat=True)
        related_terms = self.get_queryset().filter(id__in=related_ids)[:limit]
        
        serializer = TermListSerializer(related_terms, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        
        stats = {
            'total_terms': queryset.count(),
            'essential_terms': queryset.filter(is_essential=True).count(),
            'terms_by_difficulty': {},
            'terms_by_category': {},
            'total_translations': TermTranslation.objects.count(),
            'languages_available': list(
                TermTranslation.objects.values_list('language', flat=True).distinct()
            )
        }
        
        for difficulty, label in Term._meta.get_field('difficulty_level').choices:
            stats['terms_by_difficulty'][label] = queryset.filter(difficulty_level=difficulty).count()
        
        category_stats = queryset.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for item in category_stats:
            stats['terms_by_category'][item['category__name']] = item['count']
        
        return Response(stats)