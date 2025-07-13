# backend/users_roles/models/roles.py
from django.db import models
from common.models.mixins import TimestampedMixin

class Role(TimestampedMixin):
    """Rôles système pour permissions granulaires"""
    
    ROLE_TYPES = [
        ('system', 'Système'),
        ('company', 'Entreprise'),
        ('brand', 'Marque'),
        ('feature', 'Feature'),
    ]
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nom unique du rôle"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Nom d'affichage du rôle"
    )
    description = models.TextField(
        blank=True,
        help_text="Description détaillée du rôle"
    )
    
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPES,
        default='brand',
        help_text="Type de rôle"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Rôle actif"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="Rôle système (non supprimable)"
    )
    
    class Meta:
        db_table = 'role'
        ordering = ['role_type', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['role_type']),
        ]
    
    def __str__(self):
        return self.display_name

class UserRole(TimestampedMixin):
    """Association User-Role avec contexte optionnel"""
    
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text="Utilisateur"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        help_text="Rôle assigné"
    )
    
    # Contexte optionnel
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Contexte entreprise (optionnel)"
    )
    brand = models.ForeignKey(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Contexte marque (optionnel)"
    )
    feature = models.ForeignKey(
        'company_features.Feature',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Contexte feature (optionnel)"
    )
    
    # Métadonnées
    granted_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_roles',
        help_text="Utilisateur qui a accordé ce rôle"
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date d'attribution du rôle"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration du rôle"
    )
    
    class Meta:
        db_table = 'user_role'
        unique_together = ['user', 'role', 'company', 'brand', 'feature']
        indexes = [
            models.Index(fields=['user', 'role']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        context_parts = []
        if self.company:
            context_parts.append(f"Company: {self.company.name}")
        if self.brand:
            context_parts.append(f"Brand: {self.brand.name}")
        if self.feature:
            context_parts.append(f"Feature: {self.feature.name}")
        
        context = f" ({', '.join(context_parts)})" if context_parts else ""
        return f"{self.user.username} - {self.role.display_name}{context}"
    
    def is_active(self):
        """Vérifie si le rôle est actif"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() <= self.expires_at
        return True
    
    def get_context_summary(self):
        """Résumé du contexte pour l'interface"""
        return {
            'company': self.company.name if self.company else None,
            'brand': self.brand.name if self.brand else None,
            'feature': self.feature.display_name if self.feature else None,
            'is_active': self.is_active(),
            'expires_at': self.expires_at,
        }

class Permission(TimestampedMixin):
    """Permissions granulaires du système"""
    
    PERMISSION_TYPES = [
        ('read', 'Lecture'),
        ('write', 'Écriture'),
        ('delete', 'Suppression'),
        ('admin', 'Administration'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom unique de la permission"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage de la permission"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de la permission"
    )
    
    permission_type = models.CharField(
        max_length=20,
        choices=PERMISSION_TYPES,
        help_text="Type de permission"
    )
    
    # Resource context
    resource_type = models.CharField(
        max_length=50,
        help_text="Type de ressource (model, feature, etc.)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Permission active"
    )
    
    class Meta:
        db_table = 'permission'
        ordering = ['resource_type', 'permission_type', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['resource_type']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.resource_type})"

class RolePermission(TimestampedMixin):
    """Association Role-Permission"""
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        help_text="Rôle"
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles',
        help_text="Permission"
    )
    
    is_granted = models.BooleanField(
        default=True,
        help_text="Permission accordée (False = refusée explicitement)"
    )
    
    class Meta:
        db_table = 'role_permission'
        unique_together = ['role', 'permission']
        indexes = [
            models.Index(fields=['role', 'is_granted']),
        ]
    
    def __str__(self):
        grant_status = "✓" if self.is_granted else "✗"
        return f"{self.role.display_name} {grant_status} {self.permission.display_name}"
