# backend/ai_templates_core/serializers/template_serializers.py
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin

from ..models import TemplateType, BrandTemplateConfig, BaseTemplate

class TemplateTypeSerializer(DynamicFieldsSerializer):
    """Types de templates avec compteurs"""
    
    templates_count = serializers.SerializerMethodField()
    active_templates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateType
        fields = [
            'id', 'name', 'display_name', 'description', 
            'is_active', 'created_at', 'templates_count', 'active_templates_count'
        ]
    
    def get_templates_count(self, obj):
        """Total templates de ce type"""
        return obj.templates.count()
    
    def get_active_templates_count(self, obj):
        """Templates actifs de ce type"""
        return obj.templates.filter(is_active=True).count()

class BrandTemplateConfigSerializer(DynamicFieldsSerializer):
    """Configuration brand avec métriques"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    current_templates_count = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BrandTemplateConfig
        fields = [
            'id', 'brand', 'brand_name', 'max_templates_per_type',
            'max_variables_per_template', 'allow_custom_templates',
            'default_template_style', 'current_templates_count',
            'usage_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['brand']
    
    def get_current_templates_count(self, obj):
        """Nombre actuel de templates"""
        return obj.brand.ai_templates.filter(is_active=True).count()
    
    def get_usage_percentage(self, obj):
        """% d'utilisation de la limite"""
        current = self.get_current_templates_count(obj)
        return round((current / obj.max_templates_per_type * 100), 1)

class BaseTemplateListSerializer(DynamicFieldsSerializer):
    """Liste - Données essentielles uniquement"""
    
    template_type_name = serializers.CharField(source='template_type.display_name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    # Indicateurs rapides
    has_variables = serializers.SerializerMethodField()
    is_recent = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    
    # Métriques conditionnelles (si annotations disponibles)
    versions_count = serializers.IntegerField(read_only=True, default=0)
    recommendations_count = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = BaseTemplate
        fields = [
            'id', 'name', 'description', 'template_type_name', 'brand_name',
            'is_active', 'is_public', 'created_by_username', 'created_at', 'updated_at',
            'has_variables', 'is_recent', 'content_preview',
            'versions_count', 'recommendations_count'
        ]
    
    def get_has_variables(self, obj):
        """Template utilise des variables"""
        return '{{' in obj.prompt_content and '}}' in obj.prompt_content
    
    def get_is_recent(self, obj):
        """Créé dans les 7 derniers jours"""
        week_ago = timezone.now() - timedelta(days=7)
        return obj.created_at >= week_ago
    
    def get_content_preview(self, obj):
        """Aperçu du contenu (100 premiers caractères)"""
        return obj.prompt_content[:100] + "..." if len(obj.prompt_content) > 100 else obj.prompt_content

class BaseTemplateDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail - Données complètes"""
    
    template_type_name = serializers.CharField(source='template_type.display_name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    # Analyses du contenu
    content_analysis = serializers.SerializerMethodField()
    usage_metrics = serializers.SerializerMethodField()
    
    # Relations conditionnelles
    current_version = serializers.SerializerMethodField()
    workflow_status = serializers.SerializerMethodField()
    seo_config = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_name',
            'brand', 'brand_name', 'prompt_content', 'is_active', 'is_public',
            'created_by', 'created_by_username', 'created_at', 'updated_at',
            'content_analysis', 'usage_metrics', 'current_version',
            'workflow_status', 'seo_config'
        ]
        read_only_fields = ['brand', 'created_by']
        stats_fields = {
            'performance_score': 'get_performance_score'
        }
    
    def get_content_analysis(self, obj):
        """Analyse automatique du contenu"""
        content = obj.prompt_content
        
        # Comptage variables
        variable_count = content.count('{{')
        
        # Variables détectées
        import re
        variables = re.findall(r'\{\{([^}]+)\}\}', content)
        
        return {
            'character_count': len(content),
            'word_count': len(content.split()),
            'variable_count': variable_count,
            'detected_variables': list(set(variables)),
            'has_conditionals': any(keyword in content.lower() for keyword in ['if', 'unless', 'for', 'each']),
            'complexity_score': min(100, (variable_count * 10) + (len(content.split()) // 10))
        }
    
    def get_usage_metrics(self, obj):
        """Métriques d'usage (placeholder pour intégrations futures)"""
        # À connecter avec système de tracking réel
        return {
            'total_generations': 0,
            'last_used': None,
            'avg_rating': 0.0,
            'popularity_rank': 0
        }
    
    def get_current_version(self, obj):
        """Version courante si disponible"""
        try:
            if hasattr(obj, 'versions'):
                current = obj.versions.filter(is_current=True).first()
                if current:
                    return {
                        'version_number': current.version_number,
                        'created_at': current.created_at,
                        'changelog': current.changelog[:100] + "..." if len(current.changelog) > 100 else current.changelog
                    }
        except:
            pass
        return None
    
    def get_workflow_status(self, obj):
        """Status workflow si disponible"""
        try:
            if hasattr(obj, 'approvals') and obj.approvals.exists():
                latest = obj.approvals.first()
                return {
                    'status': latest.status,
                    'status_display': latest.get_status_display(),
                    'submitted_at': latest.submitted_at,
                    'reviewed_at': latest.reviewed_at
                }
        except:
            pass
        return {'status': 'draft', 'status_display': 'Brouillon'}
    
    def get_seo_config(self, obj):
        """Config SEO si disponible"""
        try:
            if hasattr(obj, 'seo_config') and obj.seo_config:
                return {
                    'page_type': obj.seo_config.page_type,
                    'search_intent': obj.seo_config.search_intent,
                    'target_word_count': obj.seo_config.target_word_count
                }
        except:
            pass
        return None
    
    def get_performance_score(self, obj):
        """Score de performance calculé"""
        score = 50  # Base
        
        # Bonus pour activité récente
        if obj.updated_at:
            days_since_update = (timezone.now() - obj.updated_at).days
            if days_since_update < 7:
                score += 30
            elif days_since_update < 30:
                score += 15
        
        # Bonus pour template public
        if obj.is_public:
            score += 10
        
        # Bonus pour description
        if obj.description and len(obj.description) > 50:
            score += 10
        
        # Bonus pour variables (complexité)
        variable_count = obj.prompt_content.count('{{')
        score += min(20, variable_count * 3)
        
        return max(0, min(100, score))

class BaseTemplateWriteSerializer(DynamicFieldsSerializer):
    """Création/modification avec validation stricte"""
    
    class Meta:
        model = BaseTemplate
        fields = [
            'name', 'description', 'template_type', 'prompt_content',
            'is_active', 'is_public'
        ]
    
    def validate_name(self, value):
        """Validation nom"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom doit contenir au moins 3 caractères")
        return value.strip()
    
    def validate_prompt_content(self, value):
        """Validation contenu prompt"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le contenu doit être plus détaillé")
        
        # Validation variables
        if '{{' in value and '}}' not in value:
            raise serializers.ValidationError("Variables mal formées - format requis: {{variable}}")
        
        # Validation longueur
        if len(value) > 10000:
            raise serializers.ValidationError("Contenu trop long (max 10000 caractères)")
        
        return value.strip()
    
    def validate(self, data):
        """Validation croisée"""
        request = self.context.get('request')
        if not request:
            return data
        
        # Vérifier unicité nom par brand + type
        name = data.get('name')
        template_type = data.get('template_type')
        brand = request.current_brand
        
        if name and template_type and brand:
            existing = BaseTemplate.objects.filter(
                brand=brand,
                name=name,
                template_type=template_type
            )
            
            # Exclure l'instance courante si update
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'name': 'Un template avec ce nom existe déjà pour ce type'
                })
        
        # Vérifier limite brand si création
        if not self.instance and template_type and brand:
            try:
                config = brand.template_config
                current_count = BaseTemplate.objects.filter(
                    brand=brand,
                    template_type=template_type,
                    is_active=True
                ).count()
                
                if current_count >= config.max_templates_per_type:
                    raise serializers.ValidationError({
                        'template_type': f'Limite de {config.max_templates_per_type} templates atteinte'
                    })
            except:
                pass  # Pas de config = pas de limite
        
        return data
    
    def create(self, validated_data):
        """Création avec brand et user automatiques"""
        request = self.context['request']
        validated_data['brand'] = request.current_brand
        validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update avec logging des changements importants"""
        content_changed = (
            'prompt_content' in validated_data and
            validated_data['prompt_content'] != instance.prompt_content
        )
        
        updated_instance = super().update(instance, validated_data)
        
        # Log si contenu modifié (pour versioning futur)
        if content_changed:
            # Placeholder pour système de versioning
            pass
        
        return updated_instance