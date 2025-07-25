# /var/www/megahub/backend/crm_activities_notes/models/notes_models.py
import uuid
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class NoteActivity(CRMBaseMixin):
    """Extension pour activités de type note - OneToOne avec Activity"""
    
    VISIBILITY_LEVELS = [
        ('private', 'Privé'),
        ('team', 'Équipe'),
        ('company', 'Entreprise'),
        ('public', 'Public'),
    ]
    
    # Relation avec Activity de base
    activity = models.OneToOneField(
        'crm_activities_core.Activity',
        on_delete=models.CASCADE,
        related_name='note_details',
        help_text="Activité de base"
    )
    
    # Contenu note
    content = models.TextField(help_text="Contenu de la note")
    content_html = models.TextField(blank=True, help_text="Contenu HTML")
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True, help_text="Tags")
    keywords = models.JSONField(default=list, blank=True, help_text="Mots-clés")
    
    # Visibilité et partage
    visibility = models.CharField(
        max_length=15,
        choices=VISIBILITY_LEVELS,
        default='private',
        help_text="Visibilité"
    )
    shared_with = models.ManyToManyField(
        'users_core.CustomUser',
        through='NoteShare',
        through_fields=('note', 'user'),
        related_name='shared_notes',
        blank=True,
        help_text="Partagé avec"
    )
    
    # Pièces jointes
    has_attachments = models.BooleanField(default=False, help_text="PJ")
    
    # Versioning
    version = models.IntegerField(default=1, help_text="Version")
    last_modified_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_notes',
        help_text="Modifié par"
    )
    
    # Interactions
    views_count = models.IntegerField(default=0, help_text="Vues")
    likes_count = models.IntegerField(default=0, help_text="Likes")
    
    # Statut
    is_pinned = models.BooleanField(default=False, help_text="Épinglé")
    is_archived = models.BooleanField(default=False, help_text="Archivé")
    archived_date = models.DateTimeField(null=True, blank=True, help_text="Date archivage")
    
    class Meta:
        db_table = 'crm_note_activity'
        verbose_name = 'Détails Note'
        verbose_name_plural = 'Détails Notes'
        indexes = [
            models.Index(fields=['visibility']),
            models.Index(fields=['is_pinned', 'is_archived']),
        ]
    
    def __str__(self):
        return f"Note - {self.activity.subject}"

class NoteShare(models.Model):
    """Partage de notes"""
    
    PERMISSION_LEVELS = [
        ('read', 'Lecture'),
        ('comment', 'Commentaire'),
        ('edit', 'Modification'),
    ]
    
    # Relations
    note = models.ForeignKey(
        NoteActivity,
        on_delete=models.CASCADE,
        help_text="Note partagée"
    )
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        help_text="Utilisateur"
    )
    
    # Configuration
    permission = models.CharField(
        max_length=10,
        choices=PERMISSION_LEVELS,
        default='read',
        help_text="Permission"
    )
    shared_date = models.DateTimeField(auto_now_add=True, help_text="Date partage")
    shared_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='shared_notes_by',
        help_text="Partagé par"
    )
    is_active = models.BooleanField(default=True, help_text="Actif")
    
    class Meta:
        db_table = 'crm_note_share'
        unique_together = ['note', 'user']
        verbose_name = 'Partage Note'
        verbose_name_plural = 'Partages Notes'
    
    def __str__(self):
        return f"{self.note.activity.subject} → {self.user.get_full_name()}"

class CommentActivity(CRMBaseMixin):
    """Extension pour activités de type commentaire - OneToOne avec Activity"""
    
    COMMENT_CATEGORIES = [
        ('general', 'Général'),
        ('feedback', 'Retour'),
        ('question', 'Question'),
        ('suggestion', 'Suggestion'),
        ('update', 'Mise à jour'),
        ('approval', 'Approbation'),
        ('rejection', 'Rejet'),
    ]
    
    # Relation avec Activity de base
    activity = models.OneToOneField(
        'crm_activities_core.Activity',
        on_delete=models.CASCADE,
        related_name='comment_details',
        help_text="Activité de base"
    )
    
    comment_category = models.CharField(
        max_length=15,
        choices=COMMENT_CATEGORIES,
        default='general',
        help_text="Catégorie"
    )
    
    # Thread de commentaires
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Commentaire parent"
    )
    thread_level = models.IntegerField(default=0, help_text="Niveau thread")
    
    # Contenu
    content = models.TextField(help_text="Contenu commentaire")
    
    # Mentions
    mentioned_users = models.ManyToManyField(
        'users_core.CustomUser',
        related_name='mentioned_in_comments',
        blank=True,
        help_text="Utilisateurs mentionnés"
    )
    
    # Réactions
    reactions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Réactions (emoji: count)"
    )
    
    # Modération
    is_flagged = models.BooleanField(default=False, help_text="Signalé")
    flagged_reason = models.CharField(max_length=100, blank=True, help_text="Raison")
    is_approved = models.BooleanField(default=True, help_text="Approuvé")
    
    # Historique édition
    is_edited = models.BooleanField(default=False, help_text="Modifié")
    edit_count = models.IntegerField(default=0, help_text="Nb modifications")
    last_edited_at = models.DateTimeField(null=True, blank=True, help_text="Dernière modif")
    
    class Meta:
        db_table = 'crm_comment_activity'
        verbose_name = 'Détails Commentaire'
        verbose_name_plural = 'Détails Commentaires'
        indexes = [
            models.Index(fields=['parent_comment', 'thread_level']),
            models.Index(fields=['comment_category']),
            models.Index(fields=['is_flagged', 'is_approved']),
        ]
    
    def __str__(self):
        return f"Commentaire - {self.activity.subject}"
