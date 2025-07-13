# backend/company_core/serializers/company_serializers.py
from rest_framework import serializers
from company_core.models.company import Company
from common.serializers.mixins import StatsMixin, RelatedFieldsMixin

class CompanySerializer(StatsMixin, RelatedFieldsMixin, serializers.ModelSerializer):
    """Serializer pour Company"""
    
    # Champs calculés
    can_add_brand = serializers.SerializerMethodField()
    can_add_user = serializers.SerializerMethodField()
    brands_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    # ✅ CORRECTION : Admin comme objet sérialisé
    admin = serializers.SerializerMethodField()
    
    # Champs relationnels optionnels
    admin_details = serializers.SerializerMethodField()
    slots_info = serializers.SerializerMethodField()
    subscription_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'admin', 'billing_email', 'description', 'url',
            'is_active', 'stripe_customer_id', 'created_at', 'updated_at',
            # Champs calculés
            'can_add_brand', 'can_add_user', 'brands_count', 'users_count',
            # Champs relationnels
            'admin_details', 'slots_info', 'subscription_info'
        ]
        read_only_fields = ['stripe_customer_id', 'created_at', 'updated_at']
        
        # Configuration pour les mixins
        stats_fields = {
            'total_brands': 'get_total_brands',
            'total_users': 'get_total_users',
            'active_brands': 'get_active_brands',
        }
    
    # ✅ CORRECTION : Nouvelle méthode pour admin
    def get_admin(self, obj):
        """Retourne les infos de l'admin au lieu de juste l'ID"""
        if obj.admin:
            return {
                'id': obj.admin.id,
                'username': obj.admin.username,
                'email': obj.admin.email,
                'first_name': obj.admin.first_name,
                'last_name': obj.admin.last_name,
            }
        return None
    
    def get_can_add_brand(self, obj):
        """Vérifie si l'entreprise peut ajouter une brand"""
        try:
            return obj.can_add_brand()
        except:
            return True  # Fallback si méthode n'existe pas
    
    def get_can_add_user(self, obj):
        """Vérifie si l'entreprise peut ajouter un utilisateur"""
        try:
            return obj.can_add_user()
        except:
            return True  # Fallback si méthode n'existe pas
    
    def get_brands_count(self, obj):
        """Nombre de brands actuelles"""
        return obj.brands.filter(is_deleted=False).count()
    
    def get_users_count(self, obj):
        """Nombre d'utilisateurs actuels"""
        return obj.members.filter(is_active=True).count()
    
    def get_admin_details(self, obj):
        """Détails de l'admin (si demandé)"""
        if 'admin_details' in self.context.get('expand', []):
            return {
                'id': obj.admin.id,
                'username': obj.admin.username,
                'email': obj.admin.email,
                'first_name': obj.admin.first_name,
                'last_name': obj.admin.last_name,
            }
        return None
    
    def get_slots_info(self, obj):
        """Informations sur les slots (si demandé)"""
        if 'slots_info' in self.context.get('expand', []):
            try:
                slots = obj.slots
                return {
                    'brands_slots': slots.brands_slots,
                    'users_slots': slots.users_slots,
                    'current_brands_count': slots.current_brands_count,
                    'current_users_count': slots.current_users_count,
                    'brands_usage_percentage': slots.get_brands_usage_percentage(),
                    'users_usage_percentage': slots.get_users_usage_percentage(),
                }
            except:
                return None
        return None
    
    def get_subscription_info(self, obj):
        """Informations sur l'abonnement (si demandé)"""
        if 'subscription_info' in self.context.get('expand', []):
            try:
                subscription = obj.subscription
                return {
                    'id': subscription.id,
                    'plan_name': subscription.plan.display_name,
                    'status': subscription.get_status_display(),
                    'current_period_end': subscription.current_period_end,
                    'amount': subscription.amount,
                    'is_active': subscription.is_active(),
                    'days_until_renewal': subscription.days_until_renewal(),
                }
            except:
                return None
        return None
    
    # Méthodes pour les stats (utilisées par StatsMixin)
    def get_total_brands(self, obj):
        return obj.brands.count()
    
    def get_total_users(self, obj):
        return obj.members.count()
    
    def get_active_brands(self, obj):
        return obj.brands.filter(is_deleted=False).count()
    
    def validate_billing_email(self, value):
        """Validation de l'email de facturation"""
        if not value:
            raise serializers.ValidationError("L'email de facturation est requis")
        return value
    
    def validate_name(self, value):
        """Validation du nom de l'entreprise"""
        if len(value) < 2:
            raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères")
        return value

class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    brands_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'billing_email', 'admin_username', 'is_active', 'created_at',
            'brands_count', 'users_count', 'plan_name'
        ]
    
    def get_brands_count(self, obj):
        return obj.brands.filter(is_deleted=False).count()
    
    def get_users_count(self, obj):
        return obj.members.filter(is_active=True).count()
    
    def get_plan_name(self, obj):
        try:
            return obj.subscription.plan.display_name
        except:
            return None

class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'entreprise"""
    
    admin_username = serializers.CharField(write_only=True)
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(write_only=True, required=False)
    admin_last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Company
        fields = [
            'name', 'billing_email', 'description', 'url',
            'admin_username', 'admin_email', 'admin_password',
            'admin_first_name', 'admin_last_name'
        ]
    
    def create(self, validated_data):
        """Crée l'entreprise et son admin"""
        from django.db import transaction
        from users_core.models.user import CustomUser
        from company_slots.models.slots import CompanySlots
        
        # Extraire les données admin
        admin_data = {
            'username': validated_data.pop('admin_username'),
            'email': validated_data.pop('admin_email'),
            'password': validated_data.pop('admin_password'),
            'first_name': validated_data.pop('admin_first_name', ''),
            'last_name': validated_data.pop('admin_last_name', ''),
            'user_type': 'agency_admin',
        }
        
        with transaction.atomic():
            # Créer l'utilisateur admin
            admin_user = CustomUser.objects.create_user(**admin_data)
            
            # Créer l'entreprise
            company = Company.objects.create(
                admin=admin_user,
                **validated_data
            )
            
            # Associer l'admin à l'entreprise
            admin_user.company = company
            admin_user.save()
            
            # Créer les slots par défaut
            CompanySlots.objects.create(company=company)
            
            return company
    
    def validate_admin_username(self, value):
        """Valide l'unicité du nom d'utilisateur admin"""
        from users_core.models.user import CustomUser
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà")
        return value
    
    def validate_admin_email(self, value):
        """Valide l'unicité de l'email admin"""
        from users_core.models.user import CustomUser
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email existe déjà")
        return value

class CompanyUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'entreprise"""
    
    class Meta:
        model = Company
        fields = ['name', 'billing_email', 'description', 'url', 'is_active']
    
    def validate_name(self, value):
        """Valide le nom de l'entreprise"""
        if len(value) < 2:
            raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères")
        return value