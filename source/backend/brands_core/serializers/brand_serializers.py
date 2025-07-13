# backend/brands_core/serializers/brand_serializers.py
from rest_framework import serializers
from brands_core.models.brand import Brand
from common.serializers.mixins import StatsMixin, RelatedFieldsMixin

class BrandSerializer(StatsMixin, RelatedFieldsMixin, serializers.ModelSerializer):
    """Serializer pour Brand"""
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    # Informations de l'admin
    brand_admin_details = serializers.SerializerMethodField()
    
    # Champs calculés
    accessible_users_count = serializers.SerializerMethodField()
    websites_count = serializers.SerializerMethodField()
    templates_count = serializers.SerializerMethodField()
    
    # Champs relationnels optionnels
    users_list = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'company', 'company_name', 'brand_admin', 'brand_admin_details',
            'name', 'description', 'url', 'is_active',
            'accessible_users_count', 'websites_count', 'templates_count',
            'users_list', 'recent_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
        # Configuration pour les mixins
        stats_fields = {
            'total_users': 'get_total_users',
            'total_websites': 'get_total_websites',
            'total_templates': 'get_total_templates',
        }
    
    def get_brand_admin_details(self, obj):
        """Détails de l'admin de la marque"""
        if obj.brand_admin:
            return {
                'id': obj.brand_admin.id,
                'username': obj.brand_admin.username,
                'email': obj.brand_admin.email,
                'first_name': obj.brand_admin.first_name,
                'last_name': obj.brand_admin.last_name,
            }
        return None
    
    def get_accessible_users_count(self, obj):
        """Nombre d'utilisateurs ayant accès à cette marque"""
        return obj.get_accessible_users().count()
    
    def get_websites_count(self, obj):
        """Nombre de sites web de cette marque"""
        # Utilise le related_name depuis seo_websites_core
        return getattr(obj, 'websites', obj.__class__.objects.none()).count()
    
    def get_templates_count(self, obj):
        """Nombre de templates de cette marque"""
        # Utilise le related_name depuis ai_templates_core
        return getattr(obj, 'ai_templates', obj.__class__.objects.none()).count()
    
    def get_users_list(self, obj):
        """Liste des utilisateurs (si demandé)"""
        if 'users_list' in self.context.get('expand', []):
            users = obj.get_accessible_users()
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'is_brand_admin': user == obj.brand_admin,
                }
                for user in users
            ]
        return None
    
    def get_recent_activity(self, obj):
        """Activité récente (si demandé)"""
        if 'recent_activity' in self.context.get('expand', []):
            # Placeholder pour l'activité récente
            return {
                'last_website_update': None,
                'last_template_created': None,
                'last_user_activity': None,
            }
        return None
    
    # Méthodes pour les stats (utilisées par StatsMixin)
    def get_total_users(self, obj):
        return obj.users.filter(is_active=True).count()
    
    def get_total_websites(self, obj):
        return getattr(obj, 'websites', obj.__class__.objects.none()).count()
    
    def get_total_templates(self, obj):
        return getattr(obj, 'ai_templates', obj.__class__.objects.none()).count()
    
    def validate_name(self, value):
        """Validation du nom de la marque"""
        if len(value) < 2:
            raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères")
        return value
    
    def validate_brand_admin(self, value):
        """Validation de l'admin de la marque"""
        if value:
            # Vérifier que l'admin appartient à la même entreprise
            company = self.initial_data.get('company') or (self.instance.company if self.instance else None)
            if company and value.company_id != company:
                raise serializers.ValidationError(
                    "L'admin de la marque doit appartenir à la même entreprise"
                )
        return value

class BrandListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    brand_admin_name = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'company', 'company_name', 'brand_admin_name',
            'url', 'is_active', 'users_count', 'created_at'
        ]
    
    def get_brand_admin_name(self, obj):
        """Nom de l'admin de la marque"""
        if obj.brand_admin:
            return f"{obj.brand_admin.first_name} {obj.brand_admin.last_name}".strip() or obj.brand_admin.username
        return None
    
    def get_users_count(self, obj):
        return obj.users.filter(is_active=True).count()

class BrandCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de marque"""
    
    class Meta:
        model = Brand
        fields = ['company', 'name', 'description', 'url', 'brand_admin']
    
    def validate(self, data):
        """Validation globale"""
        company = data['company']
        
        # Vérifier que l'entreprise peut ajouter une marque
        if not company.can_add_brand():
            try:
                slots = company.slots
                raise serializers.ValidationError(
                    f"Limite de marques atteinte ({slots.current_brands_count}/{slots.brands_slots}). "
                    f"Veuillez upgrader votre plan ou supprimer des marques existantes."
                )
            except:
                raise serializers.ValidationError(
                    "Impossible d'ajouter une marque. Limite atteinte."
                )
        
        return data
    
    def create(self, validated_data):
        """Création avec mise à jour automatique des compteurs"""
        brand = super().create(validated_data)
        
        # Le compteur est automatiquement mis à jour dans le save() du modèle
        return brand

class BrandUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour de marque"""
    
    class Meta:
        model = Brand
        fields = ['name', 'description', 'url', 'brand_admin', 'is_active']
    
    def validate_brand_admin(self, value):
        """Validation de l'admin de la marque"""
        if value and self.instance:
            # Vérifier que l'admin appartient à la même entreprise
            if value.company != self.instance.company:
                raise serializers.ValidationError(
                    "L'admin de la marque doit appartenir à la même entreprise"
                )
        return value

class BrandUserAssignmentSerializer(serializers.Serializer):
    """Serializer pour assigner des utilisateurs à une marque"""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs des utilisateurs à assigner"
    )
    
    def validate_user_ids(self, value):
        """Valide les IDs des utilisateurs"""
        if not value:
            raise serializers.ValidationError("Au moins un utilisateur doit être sélectionné")
        
        # Vérifier que tous les utilisateurs existent et appartiennent à la même entreprise
        from users_core.models.user import CustomUser
        brand = self.context['brand']
        
        users = CustomUser.objects.filter(id__in=value)
        if users.count() != len(value):
            raise serializers.ValidationError("Certains utilisateurs n'existent pas")
        
        # Vérifier que tous appartiennent à la même entreprise
        for user in users:
            if user.company != brand.company:
                raise serializers.ValidationError(
                    f"L'utilisateur {user.username} n'appartient pas à la même entreprise"
                )
        
        return value
    
    def save(self):
        """Assigne les utilisateurs à la marque"""
        brand = self.context['brand']
        user_ids = self.validated_data['user_ids']
        
        from users_core.models.user import CustomUser
        users = CustomUser.objects.filter(id__in=user_ids)
        
        # Assigner les utilisateurs
        brand.users.set(users)
        
        return brand

class BrandStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques de marque"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    stats_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'company_name', 'stats_summary', 'created_at']
    
    def get_stats_summary(self, obj):
        """Résumé des statistiques"""
        return {
            'users_count': obj.users.filter(is_active=True).count(),
            'websites_count': getattr(obj, 'websites', obj.__class__.objects.none()).count(),
            'templates_count': getattr(obj, 'ai_templates', obj.__class__.objects.none()).count(),
            'has_admin': obj.brand_admin is not None,
            'is_active': obj.is_active,
            'age_days': (obj.updated_at - obj.created_at).days,
        }
