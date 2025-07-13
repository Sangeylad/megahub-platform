# backend/glossary/admin.py
from django.contrib import admin
from django.utils.html import format_html
from glossary.models import TermCategory, Term, TermTranslation, TermRelation


@admin.register(TermCategory)
class TermCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'level_display', 'terms_count', 'color_display', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    def level_display(self, obj):
        return '  ' * obj.get_level() + str(obj.get_level())
    level_display.short_description = 'Niveau'
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; color: white; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Couleur'


class TermTranslationInline(admin.TabularInline):
    model = TermTranslation
    extra = 1
    fields = ['language', 'context', 'title', 'definition']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'difficulty_level', 'is_essential', 'popularity_score', 'is_active']
    list_filter = ['category', 'difficulty_level', 'is_essential', 'is_active']
    search_fields = ['slug', 'translations__title']
    prepopulated_fields = {'slug': ('category', )}  # Sera customisé via JS
    inlines = [TermTranslationInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('translations')


@admin.register(TermTranslation)
class TermTranslationAdmin(admin.ModelAdmin):
    list_display = ['title', 'term', 'language', 'context']
    list_filter = ['language', 'term__category']
    search_fields = ['title', 'definition', 'term__slug']


@admin.register(TermRelation)
class TermRelationAdmin(admin.ModelAdmin):
    list_display = ['from_term', 'relation_type', 'to_term', 'weight']
    list_filter = ['relation_type']
    search_fields = ['from_term__translations__title', 'to_term__translations__title']
    autocomplete_fields = ['from_term', 'to_term']