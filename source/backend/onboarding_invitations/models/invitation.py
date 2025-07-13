# backend/onboarding_invitations/models/invitation.py
# onboarding_invitations/models/invitation.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

from common.models.mixins import TimestampedMixin

class UserInvitation(TimestampedMixin):
    """Invitations d'utilisateurs dans une brand"""
    
    INVITATION_STATUS = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Relations
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text="Company qui invite"
    )
    invited_brand = models.ForeignKey(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text="Brand spécifique d'invitation"
    )
    invited_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text="User qui a envoyé l'invitation"
    )
    
    # User invité
    email = models.EmailField(
        help_text="Email de l'utilisateur invité"
    )
    accepted_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invitations',
        help_text="User qui a accepté (une fois créé)"
    )
    
    # Invitation details
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text="Token unique d'invitation"
    )
    status = models.CharField(
        max_length=20,
        choices=INVITATION_STATUS,
        default='pending',
        help_text="Status de l'invitation"
    )
    
    # User type à assigner
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('brand_member', 'Membre Marque'),
            ('brand_admin', 'Admin Marque'),
        ],
        default='brand_member',
        help_text="Type d'utilisateur à assigner"
    )
    
    # Dates
    expires_at = models.DateTimeField(
        help_text="Date d'expiration de l'invitation"
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'acceptation"
    )
    
    # Messages
    invitation_message = models.TextField(
        blank=True,
        help_text="Message personnalisé d'invitation"
    )
    
    class Meta:
        db_table = 'user_invitation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['expires_at']),
        ]
        unique_together = ['company', 'email', 'status']  # Une seule invitation pending par email/company
    
    def __str__(self):
        return f"Invitation {self.email} -> {self.invited_brand.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Set expiration par défaut"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)  # 7 jours par défaut
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Vérifie si invitation encore valide"""
        return (
            self.status == 'pending' and
            timezone.now() <= self.expires_at
        )
    
    def is_expired(self):
        """Vérifie si invitation expirée"""
        return timezone.now() > self.expires_at
    
    def mark_as_expired(self):
        """Marque comme expirée"""
        self.status = 'expired'
        self.save(update_fields=['status'])
    
    def accept(self, user):
        """
        Accepte l'invitation et configure l'user
        
        Args:
            user (CustomUser): User qui accepte
            
        Raises:
            ValueError: Si invitation invalide ou user déjà assigné
        """
        if not self.is_valid():
            raise ValueError("Invitation expirée ou déjà utilisée")
        
        if user.company is not None:
            raise ValueError(f"User {user.username} déjà assigné à company {user.company.name}")
        
        if user.email != self.email:
            raise ValueError("Email user ne correspond pas à l'invitation")
        
        from django.db import transaction
        
        with transaction.atomic():
            # Assigner user à company
            user.user_type = self.user_type
            user.company = self.company
            user.save(update_fields=['user_type', 'company'])
            
            # Assigner user à brand
            self.invited_brand.users.add(user)
            
            # Si brand_admin, mettre à jour brand
            if self.user_type == 'brand_admin':
                # Note: Garde l'admin actuel, ou logique spécifique
                pass
            
            # Marquer invitation comme acceptée
            self.status = 'accepted'
            self.accepted_by = user
            self.accepted_at = timezone.now()
            self.save(update_fields=['status', 'accepted_by', 'accepted_at'])
            
            # Assigner rôles via service
            from onboarding_invitations.services.roles_assignment import assign_invitation_roles
            assign_invitation_roles(user, self)
    
    def cancel(self):
        """Annule l'invitation"""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save(update_fields=['status'])
    
    def resend(self):
        """Renouvelle l'invitation (nouvelle expiration)"""
        if self.status in ['pending', 'expired']:
            self.status = 'pending'
            self.expires_at = timezone.now() + timedelta(days=7)
            self.save(update_fields=['status', 'expires_at'])
            
            # Renvoyer email
            from onboarding_invitations.services.email import send_invitation_email
            send_invitation_email(self)
    
    def get_invitation_url(self):
        """URL d'acceptation de l'invitation"""
        # TODO: Configurer selon front-end
        return f"/accept-invitation/{self.token}/"
    
    def get_summary(self):
        """Résumé pour API"""
        return {
            'id': self.id,
            'email': self.email,
            'status': self.status,
            'user_type': self.user_type,
            'company_name': self.company.name,
            'brand_name': self.invited_brand.name,
            'invited_by': self.invited_by.get_full_name() or self.invited_by.username,
            'expires_at': self.expires_at,
            'is_valid': self.is_valid(),
            'invitation_url': self.get_invitation_url() if self.is_valid() else None
        }