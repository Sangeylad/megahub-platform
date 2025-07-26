# /var/www/megahub/backend/mailing_lists_core/serializers/list_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin
from ..models import MailingList, ListMembership

class MailingListListSerializer(DynamicFieldsSerializer):
    """Liste des listes - champs essentiels"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MailingList
        fields = [
            'id', 'name', 'list_type', 'subscriber_count', 
            'brand_name', 'created_by_name', 'is_public', 'created_at'
        ]

class MailingListDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail complet liste avec relations"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    recent_subscribers = serializers.SerializerMethodField()
    
    class Meta:
        model = MailingList
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'subscriber_count']
        stats_fields = {
            'active_subscribers': 'get_active_subscribers_count',
            'recent_additions': 'get_recent_additions_count',
            'avg_engagement': 'get_avg_engagement_score'
        }
    
    def get_recent_subscribers(self, obj):
        """5 derniers abonnés ajoutés"""
        recent_memberships = obj.listmembership_set.select_related(
            'subscriber'
        ).order_by('-added_at')[:5]
        
        return [{
            'id': membership.subscriber.id,
            'email': membership.subscriber.email,
            'full_name': f"{membership.subscriber.first_name} {membership.subscriber.last_name}".strip(),
            'added_at': membership.added_at
        } for membership in recent_memberships]

class MailingListWriteSerializer(DynamicFieldsSerializer):
    """Serializer pour création/modification listes"""
    
    class Meta:
        model = MailingList
        fields = ['name', 'description', 'list_type', 'is_public', 'tags']
    
    def validate_name(self, value):
        """Validation nom unique par brand"""
        request = self.context.get('request')
        if not request:
            return value
            
        if self.instance:
            # Update - exclure l'instance actuelle
            qs = MailingList.objects.filter(
                name=value,
                brand=request.current_brand
            ).exclude(pk=self.instance.pk)
        else:
            # Create
            qs = MailingList.objects.filter(
                name=value,
                brand=request.current_brand
            )
        
        if qs.exists():
            raise serializers.ValidationError(
                "Une liste avec ce nom existe déjà pour cette marque."
            )
        return value

class ListMembershipSerializer(DynamicFieldsSerializer):
    """Gestion d'appartenance aux listes"""
    subscriber_email = serializers.CharField(source='subscriber.email', read_only=True)
    subscriber_name = serializers.SerializerMethodField()
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = ListMembership
        fields = [
            'id', 'subscriber', 'subscriber_email', 'subscriber_name',
            'subscription_source', 'added_by_name', 'added_at', 'is_active'
        ]
        read_only_fields = ['added_at']
    
    def get_subscriber_name(self, obj):
        return f"{obj.subscriber.first_name} {obj.subscriber.last_name}".strip()
