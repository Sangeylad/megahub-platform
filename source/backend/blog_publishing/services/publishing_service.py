# backend/blog_publishing/services/publishing_service.py

import logging
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class PublishingService:
    """Service pour workflow de publication blog"""
    
    @staticmethod
    @transaction.atomic
    def publish_article_now(article, published_by=None) -> Dict[str, Any]:
        """Publie un article immédiatement"""
        from ..models import BlogPublishingStatus
        
        # Récupérer ou créer le statut
        status, created = BlogPublishingStatus.objects.get_or_create(
            article=article,
            defaults={'status': 'draft'}
        )
        
        # Vérifications de publication
        if not status.can_be_published() and status.status != 'draft':
            raise ValidationError(f"Article ne peut pas être publié (statut: {status.status})")
        
        # Publication
        now = timezone.now()
        status.status = 'published'
        status.published_date = now
        status.last_published_date = now
        if published_by:
            status.approved_by = published_by
            status.approved_at = now
        status.save()
        
        # Mettre à jour la Page
        article.page.status = 'published'
        article.page.save(update_fields=['status'])
        
        logger.info(f"Article {article.id} publié par {published_by}")
        
        return {
            'article': article,
            'published_date': now,
            'status': 'published'
        }
    
    @staticmethod
    @transaction.atomic
    def schedule_article_publication(
        article, 
        scheduled_date, 
        scheduled_by,
        notify_author=True,
        update_social_media=False
    ) -> Dict[str, Any]:
        """Programme la publication d'un article"""
        from ..models import BlogPublishingStatus, BlogScheduledPublication
        
        if scheduled_date <= timezone.now():
            raise ValidationError("La date programmée doit être dans le futur")
        
        # Mettre à jour le statut
        status, created = BlogPublishingStatus.objects.get_or_create(
            article=article,
            defaults={'status': 'draft'}
        )
        
        status.status = 'scheduled'
        status.scheduled_date = scheduled_date
        status.save()
        
        # Créer la publication programmée
        scheduled_pub = BlogScheduledPublication.objects.create(
            article=article,
            scheduled_for=scheduled_date,
            scheduled_by=scheduled_by,
            notify_author=notify_author,
            update_social_media=update_social_media
        )
        
        logger.info(f"Article {article.id} programmé pour {scheduled_date}")
        
        return {
            'article': article,
            'scheduled_for': scheduled_date,
            'scheduled_publication_id': scheduled_pub.id
        }
    
    @staticmethod
    @transaction.atomic
    def execute_scheduled_publication(scheduled_pub_id: int) -> Dict[str, Any]:
        """Exécute une publication programmée"""
        from ..models import BlogScheduledPublication
        
        try:
            scheduled_pub = BlogScheduledPublication.objects.select_for_update().get(
                id=scheduled_pub_id
            )
            
            if not scheduled_pub.is_ready_for_execution():
                raise ValidationError("Publication non prête pour exécution")
            
            # Marquer comme en cours
            scheduled_pub.execution_status = 'processing'
            scheduled_pub.save()
            
            # Publier l'article
            result = PublishingService.publish_article_now(scheduled_pub.article)
            
            # Marquer comme terminé
            scheduled_pub.execution_status = 'completed'
            scheduled_pub.executed_at = timezone.now()
            scheduled_pub.save()
            
            # Actions post-publication
            if scheduled_pub.notify_author:
                PublishingService._notify_author(scheduled_pub.article)
            
            logger.info(f"Publication programmée {scheduled_pub_id} exécutée avec succès")
            
            return {
                'success': True,
                'article': scheduled_pub.article,
                'executed_at': scheduled_pub.executed_at
            }
            
        except Exception as e:
            # Marquer comme échec
            scheduled_pub.execution_status = 'failed'
            scheduled_pub.error_message = str(e)
            scheduled_pub.retry_count += 1
            scheduled_pub.save()
            
            logger.error(f"Échec publication programmée {scheduled_pub_id}: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'can_retry': scheduled_pub.can_retry()
            }
    
    @staticmethod
    def unpublish_article(article, unpublished_by=None) -> Dict[str, Any]:
        """Dépublie un article"""
        from ..models import BlogPublishingStatus
        
        try:
            status = article.publishing_status
        except BlogPublishingStatus.DoesNotExist:
            raise ValidationError("Article sans statut de publication")
        
        if not status.is_published():
            raise ValidationError("Article déjà non publié")
        
        # Dépublication
        status.status = 'unpublished'
        status.save()
        
        # Mettre à jour la Page
        article.page.status = 'draft'
        article.page.save(update_fields=['status'])
        
        logger.info(f"Article {article.id} dépublié par {unpublished_by}")
        
        return {
            'article': article,
            'unpublished_at': timezone.now(),
            'status': 'unpublished'
        }
    
    @staticmethod
    def get_articles_ready_for_publication():
        """Récupère les articles prêts pour publication automatique"""
        from ..models import BlogScheduledPublication
        
        return BlogScheduledPublication.objects.filter(
            execution_status='pending',
            scheduled_for__lte=timezone.now()
        ).select_related('article', 'article__page')
    
    @staticmethod
    def _notify_author(article):
        """Notifie l'auteur de la publication (placeholder)"""
        # TODO: Intégrer système de notifications
        logger.info(f"Notification envoyée à {article.primary_author.user.email}")