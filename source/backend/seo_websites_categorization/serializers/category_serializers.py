# backend/seo_websites_categorization/serializers/category_serializers.py

from rest_framework import serializers
from django.db.models import Count

from common.serializers.mixins import DynamicFieldsSerializer
from .base_serializers import SeoWebsitesCategorizationBaseSerializer
from ..models import WebsiteCategory, WebsiteCategorization

# ==================== CATEGORY SERIALIZERS ====================

class WebsiteCategoryListSerializer(DynamicFieldsSerializer):
    """Serializer pour liste catégories - données essentielles"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    websites_count = serializers.IntegerField(read_only=True)
    subcategories_count = serializers.IntegerField(read_only=True)
    full_path = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = WebsiteCategory
        fields = [
            'id', 'name', 'slug', 'color', 'parent_name', 'display_order',
            'websites_count', 'subcategories_count', 'full_path', 'level'
        ]

class WebsiteCategoryDetailSerializer(DynamicFieldsSerializer):
    """Serializer pour détail catégorie - données complètes"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    websites_count = serializers.SerializerMethodField()
    subcategories_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    recent_websites = serializers.SerializerMethodField()
    full_path = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = WebsiteCategory
        fields = '__all__'
    
    def get_websites_count(self, obj):
        if hasattr(obj, 'websites_count'):
            return obj.websites_count
        return obj.get_websites_count()
    
    def get_subcategories_count(self, obj):
        if hasattr(obj, 'subcategories_count'):
            return obj.subcategories_count
        return obj.get_subcategories_count()
    
    def get_subcategories(self, obj):
        """Sous-catégories directes"""
        subcategories = obj.subcategories.all()[:10]
        return [
            {
                'id': sub.id,
                'name': sub.name,
                'slug': sub.slug,
                'websites_count': sub.get_websites_count()
            }
            for sub in subcategories
        ]
    
    def get_recent_websites(self, obj):
        """5 derniers websites catégorisés"""
        recent_categorizations = obj.websites.select_related('website').order_by('-created_at')[:5]
        return [
            {
                'website_id': cat.website.id,
                'website_name': cat.website.name,
                'website_url': cat.website.url,
                'is_primary': cat.is_primary,
                'categorized_at': cat.created_at
            }
            for cat in recent_categorizations
        ]

class WebsiteCategoryCreateSerializer(SeoWebsitesCategorizationBaseSerializer):
    """Serializer pour création/modification catégorie"""
    
    class Meta:
        model = WebsiteCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'parent', 'display_order',  # ✅ SLUG ajouté
            'typical_da_range_min', 'typical_da_range_max', 'typical_pages_count'
        ]
        read_only_fields = ['id', 'slug']
    
    def validate_parent(self, value):
        """Validation de la hiérarchie (max 2 niveaux)"""
        if value and value.parent is not None:
            raise serializers.ValidationError(
                "Maximum 2 niveaux de hiérarchie autorisés"
            )
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier cohérence des ranges DA
        da_min = data.get('typical_da_range_min')
        da_max = data.get('typical_da_range_max')
        
        if da_min and da_max and da_min > da_max:
            raise serializers.ValidationError({
                'typical_da_range_min': 'Le minimum ne peut pas être supérieur au maximum'
            })
        
        return data

# ==================== CATEGORIZATION SERIALIZERS ====================

class WebsiteCategorizationListSerializer(DynamicFieldsSerializer):
    """Serializer pour liste catégorisations - données essentielles"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_url = serializers.CharField(source='website.url', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_full_path = serializers.CharField(source='category.get_full_path', read_only=True)
    categorized_by_username = serializers.CharField(source='categorized_by.username', read_only=True)
    
    class Meta:
        model = WebsiteCategorization
        fields = [
            'id', 'website_name', 'website_url', 'category_name', 'category_color',
            'category_full_path', 'is_primary', 'confidence_score', 'source',
            'categorized_by_username', 'created_at'
        ]

class WebsiteCategorizationDetailSerializer(DynamicFieldsSerializer):
    """Serializer pour détail catégorisation - données complètes"""
    
    website_data = serializers.SerializerMethodField()
    category_data = serializers.SerializerMethodField()
    categorized_by_data = serializers.SerializerMethodField()
    
    class Meta:
        model = WebsiteCategorization
        fields = '__all__'
    
    def get_website_data(self, obj):
        """Données complètes du website"""
        return {
            'id': obj.website.id,
            'name': obj.website.name,
            'url': obj.website.url,
            'domain_authority': obj.website.domain_authority,
            'brand_name': obj.website.brand.name,
            'pages_count': obj.website.get_pages_count()
        }
    
    def get_category_data(self, obj):
        """Données complètes de la catégorie"""
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'slug': obj.category.slug,
            'color': obj.category.color,
            'full_path': obj.category.get_full_path(),
            'level': obj.category.get_level(),
            'parent_id': obj.category.parent_id if obj.category.parent else None,
            'websites_count': obj.category.get_websites_count()
        }
    
    def get_categorized_by_data(self, obj):
        """Données de l'utilisateur qui a catégorisé"""
        if obj.categorized_by:
            return {
                'id': obj.categorized_by.id,
                'username': obj.categorized_by.username,
                'first_name': obj.categorized_by.first_name,
                'last_name': obj.categorized_by.last_name
            }
        return None

class WebsiteCategorizationCreateSerializer(SeoWebsitesCategorizationBaseSerializer):
    """Serializer pour création/modification catégorisation"""
    
    class Meta:
        model = WebsiteCategorization
        fields = [
            'id', 'website', 'category', 'is_primary', 'confidence_score',  # ✅ ID ajouté
            'source', 'notes'
        ]
        read_only_fields = ['id']  # ✅ ID en lecture seule
    
    def validate_confidence_score(self, value):
        """Validation du score de confiance"""
        if value is not None and (value < 0.0 or value > 1.0):
            raise serializers.ValidationError(
                "Le score de confiance doit être entre 0.0 et 1.0"
            )
        return value
    
    def validate(self, data):
        """Validation globale"""
        website = data.get('website')
        category = data.get('category')
        is_primary = data.get('is_primary', False)
        
        # Vérifier que l'association n'existe pas déjà
        if WebsiteCategorization.objects.filter(
            website=website, 
            category=category
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError(
                "Cette association website-catégorie existe déjà"
            )
        
        # Si is_primary=True, vérifier qu'il n'y en a pas déjà une
        if is_primary and WebsiteCategorization.objects.filter(
            website=website,
            is_primary=True
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError({
                'is_primary': 'Ce website a déjà une catégorie primaire'
            })
        
        return data