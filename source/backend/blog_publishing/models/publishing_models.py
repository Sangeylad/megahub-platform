# backend/blog_publishing/models/publishing_models.py

from django.db import models
from django.utils import timezone
from common.models.mixins import TimestampedMixin


class BlogPublishingStatus(TimestampedMixin):
    """Statut de publication détaillé pour articles"""
    article = models.OneToOneField(
        'blog_content.BlogArticle',
        on_delete=models.CASCADE,
        related_name='publishing_status'
    )
    
    PUBLICATION_STATES = [
        ('draft', 'Brouillon'),
        ('pending_review', 'En attente de relecture'),
        ('approved', 'Approuvé'),
        ('scheduled', 'Programmé'),
        ('published', 'Publié'),
        ('unpublished', 'Dépublié'),
        ('archived', 'Archivé'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=PUBLICATION_STATES,
        default='draft'
    )
    
    # Dates importantes
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de publication publique"
    )
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de publication programmée"
    )
    last_published_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière publication (historique)"
    )
    
    # Workflow
    submitted_for_review_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_articles'
    )
    
    # Flags spéciaux
    is_featured = models.BooleanField(
        default=False,
        help_text="Article mis en avant"
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Contenu premium"
    )
    is_evergreen = models.BooleanField(
        default=False,
        help_text="Contenu intemporel"
    )
    
    # Notifications
    notify_on_publish = models.BooleanField(
        default=True,
        help_text="Notifier lors de la publication"
    )
    
    def is_published(self):
        """Vérifie si l'article est effectivement publié"""
        return (
            self.status == 'published' and 
            self.published_date and 
            self.published_date <= timezone.now()
        )
    
    def can_be_published(self):
        """Vérifie si l'article peut être publié"""
        return self.status in ['approved', 'scheduled']
    
    def is_scheduled(self):
        """Vérifie si l'article est programmé"""
        return (
            self.status == 'scheduled' and 
            self.scheduled_date and 
            self.scheduled_date > timezone.now()
        )
    
    def __str__(self):
        return f"{self.article.page.title} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Statut Publication"
        verbose_name_plural = "Statuts Publication"
        db_table = 'blog_publishing_blogpublishingstatus'
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['is_featured', 'published_date']),
        ]


class BlogScheduledPublication(TimestampedMixin):
    """Publications programmées - système de queue"""
    article = models.ForeignKey(
        'blog_content.BlogArticle',
        on_delete=models.CASCADE,
        related_name='scheduled_publications'
    )
    
    scheduled_for = models.DateTimeField(
        help_text="Date/heure de publication programmée"
    )
    
    EXECUTION_STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminée'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulée'),
    ]
    
    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS,
        default='pending'
    )
    
    # Métadonnées exécution
    executed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Actions post-publication
    notify_author = models.BooleanField(default=True)
    update_social_media = models.BooleanField(default=False)
    send_newsletter = models.BooleanField(default=False)
    
    # Créé par
    scheduled_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='scheduled_publications'
    )
    
    def is_ready_for_execution(self):
        """Vérifie si prêt pour exécution"""
        return (
            self.execution_status == 'pending' and
            self.scheduled_for <= timezone.now()
        )
    
    def can_retry(self):
        """Vérifie si peut être retenté"""