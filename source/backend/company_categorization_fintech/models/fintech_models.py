# /var/www/megahub/backend/company_categorization_fintech/models/fintech_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class FintechCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises FinTech"""
    
    FINTECH_SEGMENTS = [
        ('payments', 'Paiements & Néobanques'),
        ('lending', 'Crédit & Prêts'),
        ('investment', 'Investissement & Gestion'),
        ('insurance', 'AssurTech'),
        ('regtech', 'RegTech & Compliance'),
        ('blockchain', 'Blockchain & Crypto'),
        ('robo_advisory', 'Conseil Robotisé'),
        ('crowdfunding', 'Financement Participatif'),
        ('b2b_fintech', 'Solutions B2B FinTech'),
    ]
    
    segment = models.CharField(
        max_length=20,
        choices=FINTECH_SEGMENTS,
        help_text="Segment FinTech spécialisé"
    )
    
    # Licences et régulation
    has_banking_license = models.BooleanField(
        default=False,
        help_text="Dispose d'une licence bancaire"
    )
    has_payment_license = models.BooleanField(
        default=False,
        help_text="Dispose d'une licence de paiement"
    )
    regulatory_framework = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cadre réglementaire principal (ex: PSD2, GDPR)"
    )
    
    # Métriques business FinTech
    transaction_volume_monthly = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Volume de transactions mensuel (€)"
    )
    active_users_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'utilisateurs actifs"
    )
    
    # Partenariats
    banking_partners = models.TextField(
        blank=True,
        help_text="Partenaires bancaires principaux"
    )
    payment_providers = models.TextField(
        blank=True,
        help_text="Fournisseurs de paiement intégrés"
    )
    
    # Conformité
    kyc_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="Fournisseur KYC/AML"
    )
    compliance_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Score de conformité (0-100)"
    )
    
    class Meta:
        db_table = 'fintech_company_profile'
        verbose_name = 'Profil FinTech'
        verbose_name_plural = 'Profils FinTech'
        indexes = [
            models.Index(fields=['segment']),
            models.Index(fields=['has_banking_license']),
            models.Index(fields=['compliance_score']),
        ]
    
    def get_segment_display_with_licenses(self):
        """Affichage segment avec indicateurs de licences"""
        segment = self.get_segment_display()
        licenses = []
        if self.has_banking_license:
            licenses.append("Banking")
        if self.has_payment_license:
            licenses.append("Payment")
        
        if licenses:
            return f"{segment} ({', '.join(licenses)})"
        return segment
