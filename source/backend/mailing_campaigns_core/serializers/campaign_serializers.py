# /var/www/megahub/backend/mailing_campaigns_core/serializers/campaign_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin
from ..models import Campaign, CampaignList

class CampaignListSerializer(DynamicFieldsSerializer):
    """Liste campagnes - champs essentiels"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    performance_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'campaign_type', 'status', 'total_recipients',
            'open_rate', 'click_rate', 'brand_name', 'created_by_name',
            'performance_summary', 'scheduled_send_time', 'sent_at', 'created_at'
        ]
    
    def get_performance_summary(self, obj):
        """Résumé performance simple"""
        if obj.status == 'sent':
            return {
                'sent': obj.emails_sent,
                'opened': obj.emails_opened,
                'clicked': obj.emails_clicked,
                'bounced': obj.emails_bounced
            }
        return None

class CampaignDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail complet campagne"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    target_lists_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'total_recipients', 'emails_sent',
            'emails_delivered', 'emails_opened', 'emails_clicked', 'emails_bounced',
            'emails_unsubscribed', 'open_rate', 'click_rate', 'sent_at', 'completed_at'
        ]
        stats_fields = {
            'delivery_rate': 'get_delivery_rate',
            'engagement_score': 'get_engagement_score',
            'roi_estimate': 'get_roi_estimate'
        }
    
    def get_target_lists_details(self, obj):
        """Détails des listes ciblées"""
        campaign_lists = CampaignList.objects.filter(campaign=obj).select_related('mailing_list')
        return [{
            'list_id': cl.mailing_list.id,
            'list_name': cl.mailing_list.name,
            'recipients_count': cl.recipients_count
        } for cl in campaign_lists]

class CampaignWriteSerializer(DynamicFieldsSerializer):
    """Serializer pour création/modification campagnes"""
    target_list_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        write_only=True, 
        required=False
    )
    
    class Meta:
        model = Campaign
        fields = [
            'name', 'subject_line', 'preview_text', 'campaign_type',
            'template', 'target_list_ids', 'html_content', 'text_content',
            'from_name', 'from_email', 'reply_to_email',
            'send_time_optimization', 'scheduled_send_time',
            'ab_test_enabled', 'ab_test_config', 'tags'
        ]
    
    def validate_name(self, value):
        """Validation nom unique par brand"""
        request = self.context.get('request')
        if not request:
            return value
            
        if self.instance:
            qs = Campaign.objects.filter(
                name=value,
                brand=request.current_brand
            ).exclude(pk=self.instance.pk)
        else:
            qs = Campaign.objects.filter(
                name=value,
                brand=request.current_brand
            )
        
        if qs.exists():
            raise serializers.ValidationError(
                "Une campagne avec ce nom existe déjà pour cette marque."
            )
        return value
    
    def validate_scheduled_send_time(self, value):
        """Validation date programmée"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "La date d'envoi programmée doit être dans le futur."
            )
        return value
    
    def create(self, validated_data):
        target_list_ids = validated_data.pop('target_list_ids', [])
        campaign = super().create(validated_data)
        
        # Associer les listes
        if target_list_ids:
            self._associate_lists(campaign, target_list_ids)
        
        return campaign
    
    def update(self, instance, validated_data):
        target_list_ids = validated_data.pop('target_list_ids', None)
        campaign = super().update(instance, validated_data)
        
        # MAJ des listes si fourni
        if target_list_ids is not None:
            # Supprimer anciennes associations
            CampaignList.objects.filter(campaign=campaign).delete()
            # Créer nouvelles
            self._associate_lists(campaign, target_list_ids)
        
        return campaign
    
    def _associate_lists(self, campaign, list_ids):
        """Associer listes à la campagne"""
        from mailing_lists_core.models import MailingList
        
        for list_id in list_ids:
            try:
                mailing_list = MailingList.objects.get(
                    id=list_id,
                    brand=campaign.brand
                )
                CampaignList.objects.create(
                    campaign=campaign,
                    mailing_list=mailing_list,
                    recipients_count=mailing_list.subscriber_count
                )
            except MailingList.DoesNotExist:
                continue
