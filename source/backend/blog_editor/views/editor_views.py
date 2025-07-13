# backend/blog_editor/views/editor_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from common.views.mixins import BrandScopedViewSetMixin
from rest_framework.permissions import IsAuthenticated
from common.permissions.business_permissions import IsBrandMember
from ..models import BlogContent
from ..serializers import BlogContentSerializer, BlogContentAutosaveSerializer


class BlogContentViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Contenu TipTap avec autosave et versioning"""
    queryset = BlogContent.objects.select_related(
        'article', 'article__page', 'article__primary_author', 'last_edited_by'
    )
    serializer_class = BlogContentSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Filtrage par article si spécifié"""
        queryset = super().get_queryset()
        article_id = self.request.query_params.get('article_id')
        if article_id:
            queryset = queryset.filter(article_id=article_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def autosave(self, request, pk=None):
        """Sauvegarde automatique sans increment version"""
        content = self.get_object()
        serializer = BlogContentAutosaveSerializer(
            content, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            # Sauvegarde sans incrémenter version
            serializer.save()
            return Response({
                'message': 'Autosave réussie',
                'last_autosave': timezone.now(),
                'version': content.version
            })
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['post'])
    def publish_content(self, request, pk=None):
        """Finalise le contenu et met à jour les métriques article"""
        content = self.get_object()
        
        # Met à jour word_count et reading_time dans l'article
        if content.content_text:
            word_count = len(content.content_text.split())
            reading_time = max(1, round(word_count / 250))
            
            content.article.word_count = word_count
            content.article.reading_time_minutes = reading_time
            content.article.save(update_fields=['word_count', 'reading_time_minutes'])
        
        # Incrémente version finale
        content.version += 1
        content.last_edited_by = request.user
        content.save(update_fields=['version', 'last_edited_by', 'updated_at'])
        
        return Response({
            'message': 'Contenu finalisé',
            'version': content.version,
            'word_count': content.article.word_count,
            'reading_time': content.article.reading_time_minutes
        })
    
    @action(detail=False, methods=['get'])
    def by_article(self, request):
        """Contenu par article (shortcut)"""
        article_id = request.query_params.get('article_id')
        if not article_id:
            return Response({'error': 'article_id required'}, status=400)
        
        try:
            content = self.get_queryset().get(article_id=article_id)
            serializer = self.get_serializer(content)
            return Response(serializer.data)
        except BlogContent.DoesNotExist:
            return Response({'error': 'Contenu non trouvé'}, status=404)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Templates de contenu prédéfinis"""
        templates = [
            {
                'name': 'Article Standard',
                'description': 'Structure article classique',
                'content_tiptap': {
                    'type': 'doc',
                    'content': [
                        {
                            'type': 'heading',
                            'attrs': {'level': 1},
                            'content': [{'type': 'text', 'text': 'Titre Principal'}]
                        },
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'Introduction...'}]
                        },
                        {
                            'type': 'heading',
                            'attrs': {'level': 2},
                            'content': [{'type': 'text', 'text': 'Sous-titre'}]
                        }
                    ]
                }
            },
            {
                'name': 'Article Guide',
                'description': 'Structure guide étape par étape',
                'content_tiptap': {
                    'type': 'doc',
                    'content': [
                        {
                            'type': 'heading',
                            'attrs': {'level': 1},
                            'content': [{'type': 'text', 'text': 'Guide : Titre'}]
                        },
                        {
                            'type': 'orderedList',
                            'content': [
                                {
                                    'type': 'listItem',
                                    'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Étape 1'}]}]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        return Response({'templates': templates})