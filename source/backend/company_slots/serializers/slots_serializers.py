# backend/company_slots/serializers/slots_serializers.py
from rest_framework import serializers
from company_slots.models.slots import CompanySlots

class CompanySlotsSerializer(serializers.ModelSerializer):
    """Serializer pour CompanySlots"""
    
    # Champs calculés
    brands_usage_percentage = serializers.SerializerMethodField()
    users_usage_percentage = serializers.SerializerMethodField()
    available_brands_slots = serializers.SerializerMethodField()
    available_users_slots = serializers.SerializerMethodField()
    is_brands_limit_reached = serializers.SerializerMethodField()
    is_users_limit_reached = serializers.SerializerMethodField()
    
    # Informations de l'entreprise
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CompanySlots
        fields = [
            'id', 'company', 'company_name',
            'brands_slots', 'users_slots',
            'current_brands_count', 'current_users_count',
            'brands_usage_percentage', 'users_usage_percentage',
            'available_brands_slots', 'available_users_slots',
            'is_brands_limit_reached', 'is_users_limit_reached',
            'last_brands_count_update', 'last_users_count_update',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'current_brands_count', 'current_users_count',
            'last_brands_count_update', 'last_users_count_update',
            'created_at', 'updated_at'
        ]
    
    def get_brands_usage_percentage(self, obj):
        """Pourcentage d'utilisation des slots brands"""
        return obj.get_brands_usage_percentage()
    
    def get_users_usage_percentage(self, obj):
        """Pourcentage d'utilisation des slots users"""
        return obj.get_users_usage_percentage()
    
    def get_available_brands_slots(self, obj):
        """Slots brands disponibles"""
        return obj.get_available_brands_slots()
    
    def get_available_users_slots(self, obj):
        """Slots users disponibles"""
        return obj.get_available_users_slots()
    
    def get_is_brands_limit_reached(self, obj):
        """Vérifie si la limite brands est atteinte"""
        return obj.is_brands_limit_reached()
    
    def get_is_users_limit_reached(self, obj):
        """Vérifie si la limite users est atteinte"""
        return obj.is_users_limit_reached()
    
    def validate_brands_slots(self, value):
        """Valide le nombre de slots brands"""
        if value < 1:
            raise serializers.ValidationError("Le nombre de slots brands doit être au moins 1")
        return value
    
    def validate_users_slots(self, value):
        """Valide le nombre de slots users"""
        if value < 1:
            raise serializers.ValidationError("Le nombre de slots users doit être au moins 1")
        return value

class CompanySlotsUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour des slots"""
    
    class Meta:
        model = CompanySlots
        fields = ['brands_slots', 'users_slots']
    
    def validate(self, data):
        """Validation globale"""
        instance = self.instance
        
        # Vérifier qu'on ne réduit pas en-dessous de l'usage actuel
        if 'brands_slots' in data:
            if data['brands_slots'] < instance.current_brands_count:
                raise serializers.ValidationError({
                    'brands_slots': f"Impossible de réduire à {data['brands_slots']} slots, "
                                  f"{instance.current_brands_count} brands sont actuellement utilisées"
                })
        
        if 'users_slots' in data:
            if data['users_slots'] < instance.current_users_count:
                raise serializers.ValidationError({
                    'users_slots': f"Impossible de réduire à {data['users_slots']} slots, "
                                 f"{instance.current_users_count} utilisateurs sont actuellement actifs"
                })
        
        return data

class CompanySlotsStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques des slots"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    usage_summary = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanySlots
        fields = [
            'company_name', 'usage_summary', 'warnings',
            'last_brands_count_update', 'last_users_count_update'
        ]
    
    def get_usage_summary(self, obj):
        """Résumé d'utilisation"""
        return {
            'brands': {
                'used': obj.current_brands_count,
                'total': obj.brands_slots,
                'available': obj.get_available_brands_slots(),
                'percentage': obj.get_brands_usage_percentage(),
            },
            'users': {
                'used': obj.current_users_count,
                'total': obj.users_slots,
                'available': obj.get_available_users_slots(),
                'percentage': obj.get_users_usage_percentage(),
            }
        }
    
    def get_warnings(self, obj):
        """Avertissements sur l'utilisation"""
        warnings = []
        
        brands_percentage = obj.get_brands_usage_percentage()
        users_percentage = obj.get_users_usage_percentage()
        
        if brands_percentage >= 100:
            warnings.append({
                'type': 'brands_limit',
                'message': 'Limite de marques atteinte',
                'severity': 'error'
            })
        elif brands_percentage >= 80:
            warnings.append({
                'type': 'brands_warning',
                'message': 'Limite de marques bientôt atteinte',
                'severity': 'warning'
            })
        
        if users_percentage >= 100:
            warnings.append({
                'type': 'users_limit',
                'message': "Limite d'utilisateurs atteinte",
                'severity': 'error'
            })
        elif users_percentage >= 80:
            warnings.append({
                'type': 'users_warning',
                'message': "Limite d'utilisateurs bientôt atteinte",
                'severity': 'warning'
            })
        
        return warnings
