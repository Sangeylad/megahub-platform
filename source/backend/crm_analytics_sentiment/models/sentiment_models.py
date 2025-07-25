# /var/www/megahub/backend/crm_analytics_sentiment/models/sentiment_models.py
import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_analytics_core.models import AnalyticsBaseMixin

class Sentiment(AnalyticsBaseMixin):
    """Analyse de sentiment sur contenu CRM"""
    
    SENTIMENT_SOURCES = [
        ('email', 'Email'),
        ('call_transcript', 'Transcript d\'appel'),
        ('chat', 'Chat'),
        ('note', 'Note'),
        ('review', 'Avis client'),
        ('survey', 'Enquête'),
        ('social_media', 'Réseaux sociaux'),
        ('support_ticket', 'Ticket support'),
        ('feedback', 'Feedback'),
        ('other', 'Autre'),
    ]
    
    SENTIMENT_POLARITIES = [
        ('very_negative', 'Très Négatif'),
        ('negative', 'Négatif'),
        ('neutral', 'Neutre'),
        ('positive', 'Positif'),
        ('very_positive', 'Très Positif'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source du contenu analysé
    source_type = models.CharField(
        max_length=20,
        choices=SENTIMENT_SOURCES,
        help_text="Type de source"
    )
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'entité source"
    )
    source_object_id = models.UUIDField(
        help_text="ID de l'entité source"
    )
    source_object = GenericForeignKey('source_content_type', 'source_object_id')
    
    # Contenu analysé
    analyzed_text = models.TextField(
        help_text="Texte analysé"
    )
    text_language = models.CharField(
        max_length=10,
        default='fr',
        help_text="Langue du texte"
    )
    
    # Résultats d'analyse
    sentiment_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Score de sentiment (-1 à 1)"
    )
    sentiment_polarity = models.CharField(
        max_length=15,
        choices=SENTIMENT_POLARITIES,
        help_text="Polarité du sentiment"
    )
    confidence_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score de confiance"
    )
    
    # Émotions détectées
    emotions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Émotions détectées avec scores"
    )
    dominant_emotion = models.CharField(
        max_length=20,
        blank=True,
        help_text="Émotion dominante"
    )
    
    # Analyse détaillée
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Mots-clés extraits"
    )
    topics = models.JSONField(
        default=list,
        blank=True,
        help_text="Sujets identifiés"
    )
    entities = models.JSONField(
        default=list,
        blank=True,
        help_text="Entités nommées"
    )
    
    # Métadonnées d'analyse
    analyzer_model = models.CharField(
        max_length=50,
        help_text="Modèle d'analyse utilisé"
    )
    model_version = models.CharField(
        max_length=20,
        help_text="Version du modèle"
    )
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Temps de traitement (ms)"
    )
    
    # Contexte business
    customer = models.ForeignKey(
        'crm_entities_core.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sentiment_analyses',
        help_text="Client concerné"
    )
    opportunity = models.ForeignKey(
        'crm_entities_core.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sentiment_analyses',
        help_text="Opportunité liée"
    )
    
    # Validation humaine
    human_validated = models.BooleanField(
        default=False,
        help_text="Validé par humain"
    )
    human_sentiment_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Score validé par humain"
    )
    validated_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sentiment_validations',
        help_text="Validé par"
    )
    
    class Meta:
        db_table = 'crm_analytics_sentiment'
        ordering = ['-created_at']
        verbose_name = 'Sentiment Analytics'
        verbose_name_plural = 'Sentiments Analytics'
        indexes = [
            models.Index(fields=['source_type', 'sentiment_polarity']),
            models.Index(fields=['source_content_type', 'source_object_id']),
            models.Index(fields=['sentiment_score']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['opportunity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_sentiment_polarity_display()} - {self.sentiment_score}"
    
    @property
    def sentiment_intensity(self):
        """Intensité du sentiment"""
        abs_score = abs(float(self.sentiment_score))
        if abs_score >= 0.8:
            return 'très_forte'
        elif abs_score >= 0.6:
            return 'forte'
        elif abs_score >= 0.4:
            return 'modérée'
        elif abs_score >= 0.2:
            return 'faible'
        else:
            return 'très_faible'

class TextAnalysis(AnalyticsBaseMixin):
    """Analyse textuelle avancée"""
    
    ANALYSIS_TYPES = [
        ('keyword_extraction', 'Extraction Mots-clés'),
        ('topic_modeling', 'Modélisation Sujets'),
        ('named_entity', 'Reconnaissance Entités'),
        ('intent_detection', 'Détection d\'intention'),
        ('language_detection', 'Détection Langue'),
        ('readability', 'Lisibilité'),
        ('complexity', 'Complexité'),
        ('style_analysis', 'Analyse de Style'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'entité source"
    )
    source_object_id = models.UUIDField(
        help_text="ID de l'entité source"
    )
    source_object = GenericForeignKey('source_content_type', 'source_object_id')
    
    # Configuration d'analyse
    analysis_type = models.CharField(
        max_length=20,
        choices=ANALYSIS_TYPES,
        help_text="Type d'analyse"
    )
    analyzed_text = models.TextField(
        help_text="Texte analysé"
    )
    
    # Résultats
    results = models.JSONField(
        default=dict,
        help_text="Résultats de l'analyse"
    )
    confidence_scores = models.JSONField(
        default=dict,
        blank=True,
        help_text="Scores de confiance"
    )
    
    # Métadonnées
    analyzer_config = models.JSONField(
        default=dict,
        help_text="Configuration de l'analyseur"
    )
    processing_stats = models.JSONField(
        default=dict,
        blank=True,
        help_text="Statistiques de traitement"
    )
    
    class Meta:
        db_table = 'crm_text_analysis'
        ordering = ['-created_at']
        verbose_name = 'Analyse Textuelle'
        verbose_name_plural = 'Analyses Textuelles'
        indexes = [
            models.Index(fields=['analysis_type']),
            models.Index(fields=['source_content_type', 'source_object_id']),
        ]
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.source_object}"

class CustomerSentimentProfile(AnalyticsBaseMixin):
    """Profil de sentiment agrégé par client"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(
        'crm_entities_core.Contact',
        on_delete=models.CASCADE,
        related_name='sentiment_profile',
        help_text="Client"
    )
    
    # Scores agrégés
    overall_sentiment_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Score de sentiment global"
    )
    recent_sentiment_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Score sentiment récent (30 derniers jours)"
    )
    
    # Tendances
    sentiment_trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'En amélioration'),
            ('stable', 'Stable'),
            ('declining', 'En déclin'),
            ('volatile', 'Volatile'),
        ],
        blank=True,
        help_text="Tendance du sentiment"
    )
    trend_strength = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Force de la tendance"
    )
    
    # Statistiques
    total_interactions = models.IntegerField(
        default=0,
        help_text="Nombre total d'interactions analysées"
    )
    positive_interactions = models.IntegerField(
        default=0,
        help_text="Interactions positives"
    )
    negative_interactions = models.IntegerField(
        default=0,
        help_text="Interactions négatives"
    )
    neutral_interactions = models.IntegerField(
        default=0,
        help_text="Interactions neutres"
    )
    
    # Émotions dominantes
    dominant_emotions = models.JSONField(
        default=list,
        blank=True,
        help_text="Émotions dominantes du client"
    )
    emotion_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text="Distribution des émotions"
    )
    
    # Sujets récurrents
    frequent_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="Sujets fréquemment mentionnés"
    )
    sentiment_by_topic = models.JSONField(
        default=dict,
        blank=True,
        help_text="Sentiment par sujet"
    )
    
    # Alertes
    requires_attention = models.BooleanField(
        default=False,
        help_text="Nécessite attention"
    )
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
        ],
        default='low',
        help_text="Niveau de risque"
    )
    
    class Meta:
        db_table = 'crm_customer_sentiment_profile'
        ordering = ['-overall_sentiment_score']
        verbose_name = 'Profil Sentiment Client'
        verbose_name_plural = 'Profils Sentiment Clients'
        indexes = [
            models.Index(fields=['overall_sentiment_score']),
            models.Index(fields=['sentiment_trend']),
            models.Index(fields=['requires_attention', 'risk_level']),
        ]
    
    def __str__(self):
        return f"Profil Sentiment - {self.customer.display_name}"
    
    @property
    def positivity_ratio(self):
        """Ratio de positivité"""
        if self.total_interactions == 0:
            return 0
        return (self.positive_interactions / self.total_interactions) * 100
