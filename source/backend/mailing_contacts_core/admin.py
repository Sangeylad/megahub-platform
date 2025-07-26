from django.contrib import admin

# Register your models here.
# /var/www/megahub/backend/mailing_contacts_core/admin.py

from django.contrib import admin
from .models import EmailSubscriber

@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'status', 'source', 'source_brand', 'created_at']
    list_filter = ['status', 'source', 'language', 'source_brand', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations Principales', {
            'fields': ('email', 'source_brand', 'status', 'source')
        }),
        ('Informations Personnelles', {
            'fields': ('first_name', 'last_name', 'company', 'phone')
        }),
        ('Configuration', {
            'fields': ('language', 'timezone')
        }),
        ('Relations', {
            'fields': ('crm_contact',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() if obj.first_name or obj.last_name else "-"
    full_name.short_description = "Nom complet"
