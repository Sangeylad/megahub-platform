# backend/users_core/serializers/user_serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users_core.models.user import CustomUser
from common.serializers.mixins import RelatedFieldsMixin

class CustomUserSerializer(RelatedFieldsMixin, serializers.ModelSerializer):
    """Serializer principal pour CustomUser"""
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    # Permissions et rôles
    permissions_summary = serializers.SerializerMethodField()
    accessible_brands_info = serializers.SerializerMethodField()
    
    # Champs calculés
    is_company_admin_status = serializers.SerializerMethodField()
    is_brand_admin_status = serializers.SerializerMethodField()
    
    # Champs relationnels optionnels
    brands_list = serializers.SerializerMethodField()
    administered_brands_list = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'company', 'company_name', 'user_type', 'phone', 'position',
            'is_active', 'date_joined', 'last_login', 'last_login_ip',
            'can_access_analytics', 'can_access_reports',
            'permissions_summary', 'accessible_brands_info',
            'is_company_admin_status', 'is_brand_admin_status',
            'brands_list', 'administered_brands_list',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'date_joined', 'last_login', 'last_login_ip',
            'created_at', 'updated_at'
        ]
    
    def get_permissions_summary(self, obj):
        """Résumé des permissions"""
        return obj.get_permissions_summary()
    
    def get_accessible_brands_info(self, obj):
        """Informations sur les marques accessibles"""
        brands = obj.get_accessible_brands()
        return {
            'count': brands.count(),
            'names': [brand.name for brand in brands[:5]]  # Limit to 5 for UI
        }
    
    def get_is_company_admin_status(self, obj):
        """Statut admin de l'entreprise"""
        return obj.is_company_admin()
    
    def get_is_brand_admin_status(self, obj):
        """Statut admin de marque"""
        return obj.is_brand_admin()
    
    def get_brands_list(self, obj):
        """Liste des marques accessibles (si demandé)"""
        if 'brands_list' in self.context.get('expand', []):
            brands = obj.get_accessible_brands()
            return [
                {
                    'id': brand.id,
                    'name': brand.name,
                    'is_admin': brand.brand_admin == obj,
                    'url': brand.url,
                }
                for brand in brands
            ]
        return None
    
    def get_administered_brands_list(self, obj):
        """Liste des marques administrées (si demandé)"""
        if 'administered_brands_list' in self.context.get('expand', []):
            brands = obj.get_administered_brands()
            return [
                {
                    'id': brand.id,
                    'name': brand.name,
                    'company': brand.company.name,
                    'users_count': brand.users.filter(is_active=True).count(),
                }
                for brand in brands
            ]
        return None
    
    def validate_email(self, value):
        """Validation de l'email"""
        if self.instance:
            # Lors de la mise à jour, vérifier l'unicité sauf pour l'instance actuelle
            if CustomUser.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        else:
            # Lors de la création, vérifier l'unicité
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value
    
    def validate_username(self, value):
        """Validation du nom d'utilisateur"""
        if self.instance:
            # Lors de la mise à jour, vérifier l'unicité sauf pour l'instance actuelle
            if CustomUser.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        else:
            # Lors de la création, vérifier l'unicité
            if CustomUser.objects.filter(username=value).exists():
                raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        return value

class CustomUserListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    accessible_brands_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'company_name', 'user_type', 'is_active', 'accessible_brands_count',
            'last_login', 'date_joined'
        ]
    
    def get_accessible_brands_count(self, obj):
        return obj.get_accessible_brands().count()

class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'company', 'user_type',
            'phone', 'position', 'can_access_analytics', 'can_access_reports'
        ]
    
    def validate_email(self, value):
        """Validation de l'email pour création"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value
    
    def validate_username(self, value):
        """Validation du nom d'utilisateur pour création"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier que les mots de passe correspondent
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas'
            })
        
        company = data['company']
        
        # Vérifier que l'entreprise peut ajouter un utilisateur
        if not company.can_add_user():
            try:
                slots = company.slots
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Limite d'utilisateurs atteinte ({slots.current_users_count}/{slots.users_slots}). "
                        f"Veuillez upgrader votre plan ou désactiver des utilisateurs existants."
                    ]
                })
            except:
                raise serializers.ValidationError({
                    'non_field_errors': ["Impossible d'ajouter un utilisateur. Limite atteinte."]
                })
        
        return data
    
    def create(self, validated_data):
        """Création avec hachage du mot de passe"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Le compteur est automatiquement mis à jour dans le save() du modèle
        return user

class CustomUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur"""
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'user_type',
            'phone', 'position', 'is_active',
            'can_access_analytics', 'can_access_reports'
        ]
    
    def validate_email(self, value):
        """Validation de l'email pour mise à jour"""
        if self.instance:
            if CustomUser.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value
    
    def validate_user_type(self, value):
        """Validation du type d'utilisateur"""
        # Empêcher la modification du type si l'utilisateur est admin de l'entreprise
        if self.instance and self.instance.is_company_admin():
            if value != 'agency_admin':
                raise serializers.ValidationError(
                    "Le type d'utilisateur ne peut pas être modifié pour l'admin de l'entreprise"
                )
        return value

class CustomUserPasswordChangeSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Vérifie le mot de passe actuel"""
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect")
        return value
    
    def validate(self, data):
        """Validation globale"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les nouveaux mots de passe ne correspondent pas'
            })
        return data
    
    def save(self):
        """Sauvegarde du nouveau mot de passe"""
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class CustomUserBrandAssignmentSerializer(serializers.Serializer):
    """Serializer pour assigner des marques à un utilisateur"""
    
    brand_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs des marques à assigner"
    )
    
    def validate_brand_ids(self, value):
        """Valide les IDs des marques"""
        from brands_core.models.brand import Brand
        user = self.context['user']
        
        # Vérifier que toutes les marques existent et appartiennent à la même entreprise
        brands = Brand.objects.filter(id__in=value, is_deleted=False)
        if brands.count() != len(value):
            raise serializers.ValidationError("Certaines marques n'existent pas")
        
        # Vérifier que toutes appartiennent à la même entreprise
        for brand in brands:
            if brand.company != user.company:
                raise serializers.ValidationError(
                    f"La marque {brand.name} n'appartient pas à la même entreprise"
                )
        
        return value
    
    def save(self):
        """Assigne les marques à l'utilisateur"""
        user = self.context['user']
        brand_ids = self.validated_data['brand_ids']
        
        from brands_core.models.brand import Brand
        brands = Brand.objects.filter(id__in=brand_ids, is_deleted=False)
        
        # Assigner les marques
        user.brands.set(brands)
        
        return user

class CustomUserStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques d'utilisateur"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    activity_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'company_name', 'user_type',
            'activity_summary', 'last_login', 'date_joined'
        ]
    
    def get_activity_summary(self, obj):
        """Résumé de l'activité"""
        return {
            'accessible_brands': obj.get_accessible_brands().count(),
            'administered_brands': obj.get_administered_brands().count(),
            'is_company_admin': obj.is_company_admin(),
            'is_brand_admin': obj.is_brand_admin(),
            'can_access_analytics': obj.can_access_analytics,
            'can_access_reports': obj.can_access_reports,
            'account_age_days': (obj.updated_at - obj.created_at).days,
        }