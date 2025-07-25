# /var/www/megahub/backend/crm_entities_relations/models/relation_models.py
import uuid
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class ContactRole(CRMBaseMixin):
    """Rôles des contacts dans les comptes et opportunités"""
    
    ROLE_TYPES = [
        ('decision_maker', 'Décideur'),
        ('influencer', 'Influenceur'),
        ('user', 'Utilisateur'),
        ('technical_buyer', 'Acheteur Technique'),
        ('economic_buyer', 'Acheteur Économique'),
        ('coach', 'Coach'),
        ('gatekeeper', 'Gatekeeper'),
        ('sponsor', 'Sponsor'),
    ]
    
    INVOLVEMENT_LEVELS = [
        ('primary', 'Principal'),
        ('secondary', 'Secondaire'),
        ('observer', 'Observateur'),
        ('supporter', 'Supporter'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    contact = models.ForeignKey(
        'crm_entities_core.Contact',
        on_delete=models.CASCADE,
        related_name='contact_roles',
        help_text="Contact concerné"
    )
    account = models.ForeignKey(
        'crm_entities_core.Account',
        on_delete=models.CASCADE,
        related_name='contact_roles',
        null=True,
        blank=True,
        help_text="Compte (si rôle au niveau compte)"
    )
    opportunity = models.ForeignKey(
        'crm_entities_core.Opportunity',
        on_delete=models.CASCADE,
        related_name='contact_roles',
        null=True,
        blank=True,
        help_text="Opportunité (si rôle spécifique à une affaire)"
    )
    
    # Détails du rôle
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPES,
        help_text="Type de rôle"
    )
    involvement_level = models.CharField(
        max_length=15,
        choices=INVOLVEMENT_LEVELS,
        default='primary',
        help_text="Niveau d'implication"
    )
    
    # Influence et pouvoir
    influence_score = models.IntegerField(
        default=50,
        help_text="Score d'influence (0-100)"
    )
    decision_power = models.IntegerField(
        default=50,
        help_text="Pouvoir de décision (0-100)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Rôle actif"
    )
    start_date = models.DateField(
        auto_now_add=True,
        help_text="Date début du rôle"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date fin du rôle"
    )
    
    # Notes
    description = models.TextField(
        blank=True,
        help_text="Description du rôle"
    )
    
    class Meta:
        db_table = 'crm_contact_role'
        unique_together = [
            ['contact', 'account', 'role_type'],
            ['contact', 'opportunity', 'role_type']
        ]
        ordering = ['-influence_score', '-decision_power']
        verbose_name = 'Rôle Contact'
        verbose_name_plural = 'Rôles Contacts'
        indexes = [
            models.Index(fields=['contact', 'role_type']),
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['opportunity', 'is_active']),
        ]
    
    def __str__(self):
        context = self.opportunity.name if self.opportunity else self.account.name
        return f"{self.contact.display_name} - {self.get_role_type_display()} ({context})"

class AccountHierarchy(CRMBaseMixin):
    """Hiérarchie et relations entre comptes"""
    
    RELATIONSHIP_TYPES = [
        ('parent_child', 'Parent-Enfant'),
        ('subsidiary', 'Filiale'),
        ('partner', 'Partenaire'),
        ('vendor', 'Fournisseur'),
        ('customer', 'Client'),
        ('competitor', 'Concurrent'),
        ('alliance', 'Alliance'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    parent_account = models.ForeignKey(
        'crm_entities_core.Account',
        on_delete=models.CASCADE,
        related_name='child_relationships',
        help_text="Compte parent"
    )
    child_account = models.ForeignKey(
        'crm_entities_core.Account',
        on_delete=models.CASCADE,
        related_name='parent_relationships',
        help_text="Compte enfant"
    )
    
    # Type de relation
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        help_text="Type de relation"
    )
    
    # Détails
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pourcentage de participation"
    )
    influence_level = models.IntegerField(
        default=50,
        help_text="Niveau d'influence (0-100)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Relation active"
    )
    start_date = models.DateField(
        auto_now_add=True,
        help_text="Date début relation"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date fin relation"
    )
    
    # Description
    description = models.TextField(
        blank=True,
        help_text="Description de la relation"
    )
    
    class Meta:
        db_table = 'crm_account_hierarchy'
        unique_together = ['parent_account', 'child_account', 'relationship_type']
        ordering = ['-influence_level']
        verbose_name = 'Hiérarchie Comptes'
        verbose_name_plural = 'Hiérarchies Comptes'
        indexes = [
            models.Index(fields=['parent_account', 'is_active']),
            models.Index(fields=['child_account', 'is_active']),
            models.Index(fields=['relationship_type']),
        ]
    
    def __str__(self):
        return f"{self.parent_account.name} → {self.child_account.name} ({self.get_relationship_type_display()})"

class ContactRelationship(CRMBaseMixin):
    """Relations entre contacts"""
    
    RELATIONSHIP_TYPES = [
        ('colleague', 'Collègue'),
        ('manager', 'Manager'),
        ('subordinate', 'Subordonné'),
        ('peer', 'Pair'),
        ('mentor', 'Mentor'),
        ('mentee', 'Mentoré'),
        ('business_partner', 'Partenaire Business'),
        ('referrer', 'Référent'),
        ('friend', 'Ami'),
        ('family', 'Famille'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    from_contact = models.ForeignKey(
        'crm_entities_core.Contact',
        on_delete=models.CASCADE,
        related_name='outbound_relationships',
        help_text="Contact source"
    )
    to_contact = models.ForeignKey(
        'crm_entities_core.Contact',
        on_delete=models.CASCADE,
        related_name='inbound_relationships',
        help_text="Contact cible"
    )
    
    # Type de relation
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        help_text="Type de relation"
    )
    
    # Force de la relation
    strength = models.IntegerField(
        default=50,
        help_text="Force de la relation (0-100)"
    )
    
    # Statut
    is_mutual = models.BooleanField(
        default=False,
        help_text="Relation mutuelle"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Relation active"
    )
    
    # Métadonnées
    description = models.TextField(
        blank=True,
        help_text="Description de la relation"
    )
    last_interaction = models.DateField(
        null=True,
        blank=True,
        help_text="Dernière interaction connue"
    )
    
    class Meta:
        db_table = 'crm_contact_relationship'
        unique_together = ['from_contact', 'to_contact', 'relationship_type']
        ordering = ['-strength']
        verbose_name = 'Relation Contact'
        verbose_name_plural = 'Relations Contacts'
        indexes = [
            models.Index(fields=['from_contact', 'is_active']),
            models.Index(fields=['to_contact', 'is_active']),
            models.Index(fields=['relationship_type']),
        ]
    
    def __str__(self):
        return f"{self.from_contact.display_name} → {self.to_contact.display_name} ({self.get_relationship_type_display()})"
