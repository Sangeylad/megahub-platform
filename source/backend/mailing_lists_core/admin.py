from django.contrib import admin

# Register your models here.
# /var/www/megahub/backend/mailing_lists_core/admin.py

from django.contrib import admin
from .models import MailingList, ListMembership

@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'list_type', 'subscriber_count', 'brand', 'created_by', 'is_public', 'created_at']
    list_filter = ['list_type', 'is_public', 'brand', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'subscriber_count']
    
    fieldsets = (
        ('Informations Principales', {
            'fields': ('name', 'description', 'list_type', 'brand')
        }),
        ('Configuration', {
            'fields': ('is_public', 'tags')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'subscriber_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ListMembership)
class ListMembershipAdmin(admin.ModelAdmin):
    list_display = ['subscriber_email', 'mailing_list', 'subscription_source', 'added_by', 'is_active', 'added_at']
    list_filter = ['subscription_source', 'is_active', 'added_at']
    search_fields = ['subscriber__email', 'mailing_list__name']
    readonly_fields = ['added_at']
    
    def subscriber_email(self, obj):
        return obj.subscriber.email
    subscriber_email.short_description = "Email"
