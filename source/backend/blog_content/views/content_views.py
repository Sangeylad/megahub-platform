# backend/blog_content/views/content_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from rest_framework.permissions import IsAuthenticated
from common.permissions.business_permissions import IsBrandMember
from ..models import BlogArticle, BlogAuthor, BlogTag
from ..serializers import (
    BlogArticleSerializer, 
    BlogArticleCreateSerializer,  # Ajouter
    BlogAuthorSerializer, 
    BlogTagSerializer
)
from ..filters import BlogArticleFilter


class BlogArticleViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """CRUD articles blog avec filtres avancés"""
    
    # ✅ AJOUT publishing_status dans select_related
    queryset = BlogArticle.objects.select_related(
        'page', 
        'page__website', 
        'primary_author', 
        'primary_author__user',
        'publishing_status'  # 👈 AJOUT CRUCIAL pour éviter N+1
    ).prefetch_related(
        'tags', 
        'co_authors'
    )
    
    serializer_class = BlogArticleSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogArticleFilter
    search_fields = ['page__title', 'excerpt', 'focus_keyword']
    ordering_fields = ['created_at', 'page__title', 'word_count', 'publishing_status__published_date']  # ✅ AJOUT
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Serializer différent pour création vs lecture"""
        if self.action == 'create':
            return BlogArticleCreateSerializer
        return BlogArticleSerializer
    
    # ✅ Override get_queryset pour optimisation supplémentaire si besoin
    def get_queryset(self):
        """Optimise le queryset selon l'action"""
        qs = super().get_queryset()
        
        # Pour la liste, on peut exclure certains champs lourds
        if self.action == 'list':
            # On garde tout le prefetch, c'est déjà optimisé
            pass
        
        return qs
    
    @action(detail=False, methods=['get'])
    def by_website(self, request):
        """Articles par website"""
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response({'error': 'website_id required'}, status=400)
        
        # ✅ Utilise get_queryset() pour garder les optimisations
        articles = self.get_queryset().filter(page__website_id=website_id)
        page = self.paginate_queryset(articles)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """Articles par auteur"""
        author_id = request.query_params.get('author_id')
        if not author_id:
            return Response({'error': 'author_id required'}, status=400)
        
        articles = self.get_queryset().filter(primary_author_id=author_id)
        page = self.paginate_queryset(articles)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    # ✅ BONUS : Action pour les stats par statut
    @action(detail=False, methods=['get'])
    def status_stats(self, request):
        """Statistiques par statut de publication"""
        from django.db.models import Count
        
        stats = self.get_queryset().values(
            'publishing_status__status'
        ).annotate(
            count=Count('id')
        ).order_by('publishing_status__status')
        
        # Formatter pour le frontend
        status_dict = {
            'draft': 0,
            'pending_review': 0,
            'approved': 0,
            'scheduled': 0,
            'published': 0,
            'unpublished': 0,
            'archived': 0
        }
        
        for stat in stats:
            status_key = stat['publishing_status__status']
            if status_key:
                status_dict[status_key] = stat['count']
        
        status_dict['total'] = sum(status_dict.values())
        
        return Response(status_dict)

class BlogAuthorViewSet(viewsets.ModelViewSet):
    """CRUD auteurs - filtré par company de l'utilisateur"""
    serializer_class = BlogAuthorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['display_name', 'user__username', 'user__email']
    ordering_fields = ['display_name', 'articles_count', 'created_at']
    ordering = ['display_name']
    
    def get_queryset(self):
        """Retourne uniquement les auteurs de la même company"""
        return BlogAuthor.objects.select_related('user').filter(
            user__company=self.request.user.company
        )
    
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """Users de la company avec leur statut auteur"""
        from users_core.models import CustomUser
        
        # Tous les users de la company
        company_users = CustomUser.objects.filter(
            company=request.user.company
        ).select_related('blog_author')
        
        users_data = []
        for user in company_users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'full_name': user.get_full_name() or user.username,
                'has_author_profile': hasattr(user, 'blog_author'),
                'author_id': user.blog_author.id if hasattr(user, 'blog_author') else None
            }
            users_data.append(user_info)
        
        return Response({
            'users': users_data,
            'count': len(users_data),
            'company': request.user.company.name
        })


class BlogTagViewSet(viewsets.ModelViewSet):
    """CRUD tags - globaux plateforme"""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'usage_count', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Tags les plus utilisés"""
        popular_tags = self.get_queryset().filter(
            usage_count__gt=0
        ).order_by('-usage_count')[:20]
        
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)