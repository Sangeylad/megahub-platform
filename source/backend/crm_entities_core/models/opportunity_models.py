# /var/www/megahub/backend/crm_entities_core/models/opportunity_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .base_models import CRMBaseMixin

class Opportunity(CRMBaseMixin):
    """Opportunité commerciale dans le CRM"""
    
    OPPORTUNITY_TYPES = [
        ('new_business', 'Nouvelle Affaire'),
        ('existing_customer', 'Client Existant'),
        ('renewal', 'Renouvellement'),
        ('upsell', 'Montée en Gamme'),
        ('cross_sell', 'Vente Croisée'),
    ]
    
    LEAD_SOURCES = [
        ('website', 'Site Web'),
        ('social_media', 'Réseaux Sociaux'),
        ('referral', 'Recommandation'),
        ('cold_call', 'Prospection'),
        ('trade_show', 'Salon'),
        ('webinar', 'Webinaire'),
        ('partner', 'Partenaire'),
        ('existing_customer', 'Client Existant'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200,
        help_text="Nom de l'opportunité"
    )
    opportunity_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Numéro d'opportunité auto-généré"
    )
    
    # Relations
    account = models.ForeignKey(
        'crm_entities_core.Account',
        on_delete=models.CASCADE,
        related_name='opportunities',
        help_text="Compte associé"
    )
    primary_contact = models.ForeignKey(
        'crm_entities_core.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_opportunities',
        help_text="Contact principal"
    )
    
    # Classification
    opportunity_type = models.CharField(
        max_length=20,
        choices=OPPORTUNITY_TYPES,
        default='new_business',
        help_text="Type d'opportunité"
    )
    lead_source = models.CharField(
        max_length=20,
        choices=LEAD_SOURCES,
        blank=True,
        help_text="Source du lead"
    )
    
    # Pipeline et stage
    pipeline = models.ForeignKey(
        'crm_pipeline_core.Pipeline',
        on_delete=models.CASCADE,
        help_text="Pipeline commercial"
    )
    stage = models.ForeignKey(
        'crm_pipeline_core.Stage',
        on_delete=models.CASCADE,
        help_text="Étape actuelle"
    )
    probability = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Probabilité de succès (%)"
    )
    
    # Valeurs commerciales
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Montant de l'opportunité (€)"
    )
    expected_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Revenus attendus (montant × probabilité)"
    )
    
    # Dates importantes
    close_date = models.DateField(
        help_text="Date de clôture prévue"
    )
    created_date = models.DateField(
        auto_now_add=True,
        help_text="Date de création"
    )
    discovery_completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date de fin de découverte"
    )
    proposal_sent_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date d'envoi proposition"
    )
    
    # Durée et timing
    days_in_stage = models.IntegerField(
        default=0,
        help_text="Nombre de jours dans l'étape actuelle"
    )
    sales_cycle_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée totale du cycle de vente"
    )
    
    # Informations détaillées
    description = models.TextField(
        blank=True,
        help_text="Description détaillée"
    )
    customer_need = models.TextField(
        blank=True,
        help_text="Besoin client identifié"
    )
    proposed_solution = models.TextField(
        blank=True,
        help_text="Solution proposée"
    )
    
    # Compétition
    competitors = models.TextField(
        blank=True,
        help_text="Concurrents identifiés"
    )
    competitive_advantage = models.TextField(
        blank=True,
        help_text="Avantage concurrentiel"
    )
    
    # Processus décisionnel
    decision_makers = models.TextField(
        blank=True,
        help_text="Décideurs identifiés"
    )
    decision_criteria = models.TextField(
        blank=True,
        help_text="Critères de décision"
    )
    decision_process = models.TextField(
        blank=True,
        help_text="Processus de décision"
    )
    
    # Budget et financement
    budget_confirmed = models.BooleanField(
        default=False,
        help_text="Budget confirmé"
    )
    budget_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Montant budget disponible (€)"
    )
    
    # Statut final
    is_closed = models.BooleanField(
        default=False,
        help_text="Opportunité fermée"
    )
    is_won = models.BooleanField(
        default=False,
        help_text="Opportunité gagnée"
    )
    closed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date de clôture effective"
    )
    
    # Raisons de perte
    loss_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="Raison de la perte"
    )
    loss_description = models.TextField(
        blank=True,
        help_text="Description détaillée de la perte"
    )
    
    # Next steps
    next_step = models.CharField(
        max_length=200,
        blank=True,
        help_text="Prochaine étape"
    )
    next_step_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date prochaine étape"
    )
    
    class Meta:
        db_table = 'crm_opportunity'
        ordering = ['-amount', '-close_date']
        verbose_name = 'Opportunité CRM'
        verbose_name_plural = 'Opportunités CRM'
        indexes = [
            models.Index(fields=['brand', 'stage']),
            models.Index(fields=['account']),
            models.Index(fields=['opportunity_number']),
            models.Index(fields=['close_date']),
            models.Index(fields=['amount']),
            models.Index(fields=['probability']),
            models.Index(fields=['is_closed', 'is_won']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.account.name} ({self.amount}€)"
    
    def save(self, *args, **kwargs):
        # Auto-générer le numéro d'opportunité
        if not self.opportunity_number:
            last_opp = Opportunity.objects.filter(
                brand=self.brand
            ).order_by('created_at').last()
            
            if last_opp and last_opp.opportunity_number:
                try:
                    last_number = int(last_opp.opportunity_number.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.opportunity_number = f"OPP-{new_number:06d}"
        
        # Calculer les revenus attendus
        if self.amount and self.probability:
            self.expected_revenue = self.amount * (self.probability / 100)
        
        # Calculer les jours dans l'étape
        if self.pk:  # Mise à jour d'une opportunité existante
            try:
                old_opp = Opportunity.objects.get(pk=self.pk)
                if old_opp.stage != self.stage:
                    # Changement d'étape, reset du compteur
                    self.days_in_stage = 0
                else:
                    # Même étape, calculer la durée
                    if old_opp.updated_at:
                        delta = timezone.now() - old_opp.updated_at
                        self.days_in_stage = delta.days
            except Opportunity.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def age_in_days(self):
        """Âge de l'opportunité en jours"""
        return (timezone.now().date() - self.created_date).days
    
    @property
    def is_overdue(self):
        """Vérifie si l'opportunité est en retard"""
        return not self.is_closed and self.close_date < timezone.now().date()
    
    @property
    def days_to_close(self):
        """Nombre de jours avant la date de clôture"""
        if self.is_closed:
            return 0
        return (self.close_date - timezone.now().date()).days
    
    def mark_as_won(self):
        """Marque l'opportunité comme gagnée"""
        self.is_closed = True
        self.is_won = True
        self.closed_date = timezone.now().date()
        self.probability = 100
        self.save(update_fields=['is_closed', 'is_won', 'closed_date', 'probability'])
    
    def mark_as_lost(self, reason="", description=""):
        """Marque l'opportunité comme perdue"""
        self.is_closed = True
        self.is_won = False
        self.closed_date = timezone.now().date()
        self.probability = 0
        if reason:
            self.loss_reason = reason
        if description:
            self.loss_description = description
        self.save(update_fields=[
            'is_closed', 'is_won', 'closed_date', 'probability',
            'loss_reason', 'loss_description'
        ])
