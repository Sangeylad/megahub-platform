# /var/www/megahub/backend/crm_activities_communication/models/communication_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_entities_core.models import CRMBaseMixin

class CommunicationActivity(CRMBaseMixin):
    """Extension pour activités de communication - OneToOne avec Activity"""
    
    # Relation avec Activity de base
    activity = models.OneToOneField(
        'crm_activities_core.Activity',
        on_delete=models.CASCADE,
        related_name='communication_details',
        help_text="Activité de base"
    )
    
    # Champs communs communication
    external_reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID externe (système téléphonie, email)"
    )
    provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Fournisseur (Zoom, Gmail, etc.)"
    )
    
    # Enregistrement/Archive
    has_recording = models.BooleanField(
        default=False,
        help_text="Enregistrement disponible"
    )
    recording_url = models.URLField(
        blank=True,
        help_text="URL enregistrement"
    )
    
    class Meta:
        db_table = 'crm_communication_activity'
        verbose_name = 'Détails Communication'
        verbose_name_plural = 'Détails Communications'
    
    def __str__(self):
        return f"Communication - {self.activity.subject}"

class CallActivity(CRMBaseMixin):
    """Extension spécialisée pour appels - OneToOne avec CommunicationActivity"""
    
    CALL_TYPES = [
        ('inbound', 'Entrant'),
        ('outbound', 'Sortant'),
        ('missed', 'Manqué'),
    ]
    
    CALL_OUTCOMES = [
        ('answered', 'Répondu'),
        ('no_answer', 'Pas de réponse'),
        ('voicemail', 'Messagerie'),
        ('busy', 'Occupé'),
        ('disconnected', 'Raccroché'),
        ('callback_requested', 'Rappel demandé'),
    ]
    
    # Relation avec CommunicationActivity
    communication = models.OneToOneField(
        CommunicationActivity,
        on_delete=models.CASCADE,
        related_name='call_details',
        help_text="Détails communication"
    )
    
    # Spécifique appels
    phone_number = models.CharField(
        max_length=20,
        help_text="Numéro de téléphone"
    )
    contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nom du contact"
    )
    call_type = models.CharField(
        max_length=15,
        choices=CALL_TYPES,
        help_text="Type d'appel"
    )
    call_outcome = models.CharField(
        max_length=20,
        choices=CALL_OUTCOMES,
        blank=True,
        help_text="Résultat"
    )
    
    # Timing appel
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Durée (secondes)"
    )
    call_start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Début"
    )
    call_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fin"
    )
    
    # Qualité
    call_quality = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Qualité (1-5)"
    )
    
    class Meta:
        db_table = 'crm_call_activity'
        verbose_name = 'Détails Appel'
        verbose_name_plural = 'Détails Appels'
    
    def __str__(self):
        return f"Appel {self.get_call_type_display()} - {self.contact_name or self.phone_number}"

class EmailActivity(CRMBaseMixin):
    """Extension spécialisée pour emails"""
    
    EMAIL_TYPES = [
        ('outbound', 'Sortant'),
        ('inbound', 'Entrant'),
        ('reply', 'Réponse'),
        ('forward', 'Transfert'),
    ]
    
    # Relation avec CommunicationActivity
    communication = models.OneToOneField(
        CommunicationActivity,
        on_delete=models.CASCADE,
        related_name='email_details',
        help_text="Détails communication"
    )
    
    # Headers email
    from_email = models.EmailField(help_text="Expéditeur")
    to_emails = models.JSONField(default=list, help_text="Destinataires")
    cc_emails = models.JSONField(default=list, blank=True, help_text="Copie")
    bcc_emails = models.JSONField(default=list, blank=True, help_text="Copie cachée")
    
    email_type = models.CharField(
        max_length=15,
        choices=EMAIL_TYPES,
        help_text="Type d'email"
    )
    
    # Contenu
    body_text = models.TextField(blank=True, help_text="Corps texte")
    body_html = models.TextField(blank=True, help_text="Corps HTML")
    
    # Métadonnées
    has_attachments = models.BooleanField(default=False, help_text="Pièces jointes")
    attachments_count = models.IntegerField(default=0, help_text="Nombre PJ")
    
    # Tracking
    is_opened = models.BooleanField(default=False, help_text="Ouvert")
    opened_date = models.DateTimeField(null=True, blank=True, help_text="Date ouverture")
    open_count = models.IntegerField(default=0, help_text="Nb ouvertures")
    is_replied = models.BooleanField(default=False, help_text="Répondu")
    
    # Thread
    thread_id = models.CharField(max_length=255, blank=True, help_text="Thread ID")
    in_reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies',
        help_text="En réponse à"
    )
    
    class Meta:
        db_table = 'crm_email_activity'
        verbose_name = 'Détails Email'
        verbose_name_plural = 'Détails Emails'
    
    def __str__(self):
        return f"Email {self.get_email_type_display()}: {self.communication.activity.subject}"

class MeetingActivity(CRMBaseMixin):
    """Extension spécialisée pour réunions"""
    
    MEETING_TYPES = [
        ('in_person', 'En personne'),
        ('video_call', 'Visioconférence'),
        ('phone_call', 'Téléconférence'),
        ('webinar', 'Webinaire'),
    ]
    
    # Relation avec CommunicationActivity
    communication = models.OneToOneField(
        CommunicationActivity,
        on_delete=models.CASCADE,
        related_name='meeting_details',
        help_text="Détails communication"
    )
    
    meeting_type = models.CharField(
        max_length=20,
        choices=MEETING_TYPES,
        help_text="Type de réunion"
    )
    
    # Timing
    start_time = models.DateTimeField(help_text="Début")
    end_time = models.DateTimeField(help_text="Fin")
    timezone = models.CharField(
        max_length=50, 
        default='Europe/Paris', 
        help_text="Fuseau horaire"
    )
    
    # Lieu physique
    meeting_room = models.CharField(max_length=100, blank=True, help_text="Salle")
    
    # Visioconférence
    meeting_url = models.URLField(blank=True, help_text="URL réunion")
    meeting_id = models.CharField(max_length=50, blank=True, help_text="ID réunion")
    passcode = models.CharField(max_length=20, blank=True, help_text="Code")
    
    # Contenu
    agenda = models.TextField(blank=True, help_text="Ordre du jour")
    meeting_notes = models.TextField(blank=True, help_text="Notes")
    action_items = models.JSONField(default=list, blank=True, help_text="Actions")
    decisions_made = models.JSONField(default=list, blank=True, help_text="Décisions")
    
    # Participants externes
    external_participants = models.JSONField(
        default=list, 
        blank=True, 
        help_text="Participants externes"
    )
    
    class Meta:
        db_table = 'crm_meeting_activity'
        verbose_name = 'Détails Réunion'
        verbose_name_plural = 'Détails Réunions'
    
    def __str__(self):
        return f"Réunion {self.get_meeting_type_display()}: {self.communication.activity.subject}"
