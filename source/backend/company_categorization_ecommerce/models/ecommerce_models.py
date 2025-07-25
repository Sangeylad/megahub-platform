# /var/www/megahub/backend/company_categorization_ecommerce/models/ecommerce_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class EcommerceCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises e-commerce"""
    
    BUSINESS_MODELS = [
        ('b2c', 'B2C - Business to Consumer'),
        ('b2b', 'B2B - Business to Business'),
        ('c2c', 'C2C - Consumer to Consumer'),
        ('marketplace', 'Marketplace'),
        ('dropshipping', 'Dropshipping'),
        ('subscription', 'Commerce par Abonnement'),
        ('rental', 'Location/Rental'),
        ('digital_products', 'Produits Digitaux'),
    ]
    
    PRODUCT_CATEGORIES = [
        ('fashion', 'Mode & Accessoires'),
        ('electronics', 'Électronique & High-Tech'),
        ('home_garden', 'Maison & Jardin'),
        ('health_beauty', 'Santé & Beauté'),
        ('sports', 'Sport & Loisirs'),
        ('food_beverage', 'Alimentaire & Boissons'),
        ('books_media', 'Livres & Médias'),
        ('automotive', 'Automobile'),
        ('baby_kids', 'Bébé & Enfants'),
        ('services', 'Services'),
        ('multi_category', 'Multi-catégories'),
    ]
    
    business_model = models.CharField(
        max_length=20,
        choices=BUSINESS_MODELS,
        help_text="Modèle business e-commerce"
    )
    primary_category = models.CharField(
        max_length=20,
        choices=PRODUCT_CATEGORIES,
        help_text="Catégorie produits principale"
    )
    
    # Plateforme e-commerce
    ecommerce_platform = models.CharField(
        max_length=50,
        blank=True,
        help_text="Plateforme e-commerce (Shopify, Magento, WooCommerce)"
    )
    has_mobile_app = models.BooleanField(
        default=False,
        help_text="Dispose d'une application mobile"
    )
    has_physical_stores = models.BooleanField(
        default=False,
        help_text="Possède des magasins physiques"
    )
    
    # Métriques business
    monthly_visitors = models.IntegerField(
        null=True,
        blank=True,
        help_text="Visiteurs mensuels sur le site"
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taux de conversion (%)"
    )
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Panier moyen (€)"
    )
    monthly_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="CA mensuel estimé (€)"
    )
    
    # Catalogue
    products_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de produits au catalogue"
    )
    has_own_brand = models.BooleanField(
        default=False,
        help_text="Vend sa propre marque"
    )
    is_reseller = models.BooleanField(
        default=False,
        help_text="Revend des marques tierces"
    )
    
    # Logistique
    fulfillment_model = models.CharField(
        max_length=50,
        blank=True,
        help_text="Modèle de fulfillment (own, 3PL, dropship)"
    )
    shipping_zones = models.TextField(
        blank=True,
        help_text="Zones de livraison"
    )
    same_day_delivery = models.BooleanField(
        default=False,
        help_text="Livraison le jour même disponible"
    )
    
    # Marketing & acquisition
    primary_traffic_source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source de trafic principale (SEO, Ads, Social)"
    )
    uses_influencer_marketing = models.BooleanField(
        default=False,
        help_text="Utilise le marketing d'influence"
    )
    loyalty_program = models.BooleanField(
        default=False,
        help_text="Programme de fidélité en place"
    )
    
    # Paiement
    payment_methods = models.TextField(
        blank=True,
        help_text="Méthodes de paiement acceptées"
    )
    supports_bnpl = models.BooleanField(
        default=False,
        help_text="Supporte le paiement en plusieurs fois"
    )
    
    class Meta:
        db_table = 'ecommerce_company_profile'
        verbose_name = 'Profil E-commerce'
        verbose_name_plural = 'Profils E-commerce'
        indexes = [
            models.Index(fields=['business_model']),
            models.Index(fields=['primary_category']),
            models.Index(fields=['has_physical_stores']),
        ]
    
    def get_business_summary(self):
        """Résumé du business model"""
        omnichannel = " + Magasins" if self.has_physical_stores else ""
        mobile = " + App Mobile" if self.has_mobile_app else ""
        return f"{self.get_business_model_display()}{omnichannel}{mobile}"
