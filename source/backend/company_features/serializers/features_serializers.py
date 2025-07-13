# backend/company_features/serializers/features_serializers.py
from rest_framework import serializers
from company_features.models.features import Feature, CompanyFeature

class FeatureSerializer(serializers.ModelSerializer):
    """Serializer pour Feature"""
    
    subscribed_companies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Feature
        fields = [
            'id', 'name', 'display_name', 'description', 'feature_type',
            'is_active', 'is_premium', 'sort_order', 'created_at', 'updated_at',
            'subscribed_companies_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subscribed_companies_count(self, obj):
        """Nombre d'entreprises abonnées à cette feature"""
        return obj.subscribed_companies.filter(is_enabled=True).count()

class CompanyFeatureSerializer(serializers.ModelSerializer):
    """Serializer pour CompanyFeature"""
    
    # Informations de la feature
    feature_name = serializers.CharField(source='feature.display_name', read_only=True)
    feature_type = serializers.CharField(source='feature.feature_type', read_only=True)
    feature_description = serializers.CharField(source='feature.description', read_only=True)
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    # Champs calculés
    is_active_status = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    is_usage_limit_reached_status = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyFeature
        fields = [
            'id', 'company', 'company_name', 'feature', 'feature_name', 
            'feature_type', 'feature_description',
            'is_enabled', 'usage_limit', 'current_usage',
            'subscribed_at', 'expires_at',
            'is_active_status', 'usage_percentage', 'is_usage_limit_reached_status',
            'days_until_expiry', 'created_at', 'updated_at'
        ]
        read_only_fields = ['subscribed_at', 'created_at', 'updated_at']
    
    def get_is_active_status(self, obj):
        """Statut d'activation de la feature"""
        return obj.is_active()
    
    def get_usage_percentage(self, obj):
        """Pourcentage d'utilisation"""
        return obj.get_usage_percentage()
    
    def get_is_usage_limit_reached_status(self, obj):
        """Limite d'utilisation atteinte"""
        return obj.is_usage_limit_reached()
    
    def get_days_until_expiry(self, obj):
        """Nombre de jours avant expiration"""
        if not obj.expires_at:
            return None
        
        from django.utils import timezone
        delta = obj.expires_at - timezone.now()
        return delta.days if delta.days > 0 else 0
    
    def validate_usage_limit(self, value):
        """Valide la limite d'utilisation"""
        if value is not None and value < 0:
            raise serializers.ValidationError("La limite d'utilisation ne peut pas être négative")
        return value
    
    def validate_current_usage(self, value):
        """Valide l'utilisation actuelle"""
        if value < 0:
            raise serializers.ValidationError("L'utilisation actuelle ne peut pas être négative")
        return value

class CompanyFeatureListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes de features d'entreprise"""
    
    feature_name = serializers.CharField(source='feature.display_name', read_only=True)
    feature_type = serializers.CharField(source='feature.feature_type', read_only=True)
    is_active_status = serializers.SerializerMethodField()
    usage_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyFeature
        fields = [
            'id', 'feature', 'feature_name', 'feature_type',
            'is_enabled', 'is_active_status', 'usage_info', 'expires_at'
        ]
    
    def get_is_active_status(self, obj):
        return obj.is_active()
    
    def get_usage_info(self, obj):
        """Informations d'utilisation condensées"""
        if obj.usage_limit is None:
            return {'unlimited': True}
        
        return {
            'unlimited': False,
            'current': obj.current_usage,
            'limit': obj.usage_limit,
            'percentage': obj.get_usage_percentage(),
            'limit_reached': obj.is_usage_limit_reached()
        }

class CompanyFeatureCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une association Company-Feature"""
    
    class Meta:
        model = CompanyFeature
        fields = ['company', 'feature', 'is_enabled', 'usage_limit', 'expires_at']
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier qu'il n'y a pas déjà une association
        if CompanyFeature.objects.filter(
            company=data['company'],
            feature=data['feature']
        ).exists():
            raise serializers.ValidationError(
                "Cette entreprise est déjà abonnée à cette feature"
            )
        
        return data

class CompanyFeatureUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une association Company-Feature"""
    
    class Meta:
        model = CompanyFeature
        fields = ['is_enabled', 'usage_limit', 'expires_at']
    
    def validate_usage_limit(self, value):
        """Valide que la nouvelle limite n'est pas inférieure à l'usage actuel"""
        if value is not None and self.instance:
            if value < self.instance.current_usage:
                raise serializers.ValidationError(
                    f"La limite ne peut pas être inférieure à l'utilisation actuelle ({self.instance.current_usage})"
                )
        return value

class FeatureUsageSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisation des features"""
    
    feature_name = serializers.CharField(source='feature.display_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyFeature
        fields = [
            'company_name', 'feature_name', 'current_usage', 'usage_limit',
            'usage_stats', 'updated_at'
        ]
        read_only_fields = ['company_name', 'feature_name', 'updated_at']
    
    def get_usage_stats(self, obj):
        """Statistiques d'utilisation"""
        return {
            'percentage': obj.get_usage_percentage(),
            'remaining': obj.usage_limit - obj.current_usage if obj.usage_limit else None,
            'is_unlimited': obj.usage_limit is None,
            'is_limit_reached': obj.is_usage_limit_reached(),
            'days_until_reset': None,  # À implémenter selon la logique métier
        }

class CompanyFeaturesOverviewSerializer(serializers.Serializer):
    """Serializer pour une vue d'ensemble des features d'une entreprise"""
    
    company_id = serializers.IntegerField()
    company_name = serializers.CharField()
    total_features = serializers.IntegerField()
    active_features = serializers.IntegerField()
    premium_features = serializers.IntegerField()
    features_expiring_soon = serializers.IntegerField()
    features_over_limit = serializers.IntegerField()
    
    def to_representation(self, company):
        """Calcule les statistiques pour une entreprise"""
        features = company.company_features.all()
        
        total_features = features.count()
        active_features = features.filter(is_enabled=True).count()
        premium_features = features.filter(feature__is_premium=True).count()
        
        # Features expirant dans les 30 jours
        from django.utils import timezone
        from datetime import timedelta
        thirty_days = timezone.now() + timedelta(days=30)
        features_expiring_soon = features.filter(
            expires_at__lte=thirty_days,
            expires_at__gt=timezone.now()
        ).count()
        
        # Features au-dessus de la limite
        features_over_limit = sum(1 for f in features if f.is_usage_limit_reached())
        
        return {
            'company_id': company.id,
            'company_name': company.name,
            'total_features': total_features,
            'active_features': active_features,
            'premium_features': premium_features,
            'features_expiring_soon': features_expiring_soon,
            'features_over_limit': features_over_limit,
        }
