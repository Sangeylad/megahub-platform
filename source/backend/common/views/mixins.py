# backend/common/views/mixins.py
# /var/www/megahub/backend/common/mixins/viewset_mixins.py

from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class BrandScopedViewSetMixin:
    """Mixin pour scope automatique par brand - Version rétrocompatible"""
    
    # ✅ GARDE TON CODE ACTUEL get_queryset() INTACT
    def get_queryset(self):
        """Filtre automatique par brand accessible"""
        try:
            queryset = super().get_queryset()
        except AssertionError:
            if hasattr(self, 'serializer_class') and hasattr(self.serializer_class.Meta, 'model'):
                queryset = self.serializer_class.Meta.model.objects.all()
            else:
                raise AssertionError('Définir queryset ou serializer_class avec Meta.model')
        
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.none()
        
        # Company admin : accès total
        if hasattr(user, 'is_company_admin') and user.is_company_admin():
            return queryset
        
        if not hasattr(user, 'brands'):
            return queryset.none()
        
        accessible_brands = user.brands.all()
        accessible_brand_ids = list(accessible_brands.values_list('id', flat=True))
        
        if not accessible_brand_ids:
            return queryset.none()
        
        # Filtrage intelligent selon le modèle
        model = queryset.model
        brand_filter = self._get_brand_filter_for_model(model)
        
        # ✅ PROTECTION : Si pas de brand_filter trouvé, pas de filtrage
        if brand_filter is None:
            return queryset
        
        return queryset.filter(**{f"{brand_filter}__in": accessible_brand_ids})
    
    # ✅ GARDE TON MAPPING ACTUEL ET AJOUTE JUSTE LES BLOGS
    def _get_brand_filter_for_model(self, model):
        """Détermine le chemin de filtrage vers Brand selon le modèle"""
        model_name = model.__name__.lower()
        
        brand_filters = {
            # seo_websites_core
            'website': 'brand',
            'websitesyncstatus': 'website__brand',
            
            # seo_pages_content  
            'page': 'website__brand',
            'pagetemplate': 'brand',
            
            # seo_pages_hierarchy
            'pagehierarchy': 'page__website__brand',
            'pagebreadcrumb': 'page__website__brand',
            
            # seo_pages_layout
            'pagelayout': 'page__website__brand', 
            'pagesection': 'page__website__brand',
            
            # seo_pages_workflow
            'pagestatus': 'page__website__brand',
            'pageworkflowhistory': 'page__website__brand',
            
            # seo_pages_seo
            'pageseo': 'page__website__brand',
            'pageperformance': 'page__website__brand',
            
            # seo_pages_keywords
            'pagekeyword': 'page__website__brand',
            
            # BLOG MODELS
            'blogcollection': 'brand',
            'blogcollectionitem': 'collection__brand',
            'blogarticle': 'page__website__brand',
            'blogauthor': 'user__company',
            'blogtag': None,  # Global, pas de scope
            'blogconfig': 'website__brand',
            'blogcontent': 'article__page__website__brand',
            'blogpublishingstatus': 'article__page__website__brand',
            
            # ✅ AJOUTER LES MODÈLES IA
            'aijobtype': None,  # Global, pas de scope
            'aijob': 'brand',  # Direct brand scope
            'aijobusage': 'ai_job__brand',  # Via AIJob
            'aiusagealert': 'company',  # Via company
            'aiprovider': None,  # Global
            'aicredentials': 'brand',  # Direct brand scope
            'openaiusage': 'brand',  # Usage par brand
            'chatconversation': 'brand', 
            # Legacy/autres modèles
            'keyword': 'brand',
            'semanticcocoon': 'brand',
        }
        
        return brand_filters.get(model_name, 'brand')
    
    def perform_create(self, serializer):
        """✅ VERSION RÉTROCOMPATIBLE - Support ancien + nouveau"""
        current_brand = getattr(self.request, 'current_brand', None)
        
        if current_brand:
            # Détermine comment assigner la brand selon le modèle
            model = serializer.Meta.model
            brand_assignment = self._get_brand_assignment_for_model(model)
            
            if brand_assignment:
                serializer.save(**{brand_assignment: current_brand})
            else:
                super().perform_create(serializer)
        else:
            # ✅ FALLBACK : Si pas de current_brand, comportement normal
            # Ton ancien code continue de marcher
            super().perform_create(serializer)
    
    def _get_brand_assignment_for_model(self, model):
        """Détermine comment assigner la brand lors de la création"""
        model_name = model.__name__.lower()
        
        assignments = {
            'website': 'brand',
            'page': None,  # Gestion spéciale via website_id
            'blogcollection': 'brand',  # ✅ NOUVEAU
            'blogconfig': None,
            'blogarticle': None,
        }
        
        return assignments.get(model_name)

class BulkActionViewSetMixin:
    """
    Mixin pour actions en masse
    
    Ajoute des endpoints bulk standards
    """
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        POST /items/bulk-update/
        
        Mise à jour en masse
        Body: {
            "ids": [1, 2, 3],
            "updates": {"field": "value"}
        }
        """
        ids = request.data.get('ids', [])
        updates = request.data.get('updates', {})
        
        if not ids or not updates:
            return Response(
                {'error': 'ids et updates sont requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        updated_count = queryset.update(**updates)
        
        return Response({
            'updated_count': updated_count,
            'message': f'{updated_count} éléments mis à jour'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        POST /items/bulk-delete/
        
        Suppression en masse (logique si supportée)
        Body: {"ids": [1, 2, 3]}
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': 'ids est requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        
        # Soft delete si supporté
        if hasattr(queryset.model, 'soft_delete'):
            for item in queryset:
                item.soft_delete(user=request.user)
            deleted_count = len(ids)
        else:
            deleted_count, _ = queryset.delete()
        
        return Response({
            'deleted_count': deleted_count,
            'message': f'{deleted_count} éléments supprimés'
        })

class AnalyticsViewSetMixin:
    """
    Mixin pour endpoints analytics standards
    
    Ajoute des actions de stats communes
    """
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /items/stats/
        
        Statistiques générales du modèle
        """
        queryset = self.get_queryset()
        
        total_items = queryset.count()
        
        # Stats par période si timestamps disponibles
        stats = {'total_items': total_items}
        
        if hasattr(queryset.model, 'created_at'):
            from datetime import timedelta
            
            last_30_days = timezone.now() - timedelta(days=30)
            recent_items = queryset.filter(created_at__gte=last_30_days).count()
            stats['recent_items'] = recent_items
            stats['growth_rate'] = (recent_items / total_items * 100) if total_items > 0 else 0
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        GET /items/dashboard/
        
        Vue dashboard avec top items et résumé
        """
        queryset = self.get_queryset()
        
        # Top 5 items les plus récents
        recent_items = queryset.order_by('-created_at')[:5] if hasattr(queryset.model, 'created_at') else queryset[:5]
        
        return Response({
            'total_count': queryset.count(),
            'recent_items': self.get_serializer(recent_items, many=True).data,
            'generated_at': timezone.now().isoformat()
        })

class ExportViewSetMixin:
    """
    Mixin pour export de données
    
    Endpoints d'export en différents formats
    """
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        GET /items/export-csv/
        
        Export CSV des données filtrées
        """
        import csv
        from django.http import HttpResponse
        
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.basename}.csv"'
        
        writer = csv.writer(response)
        
        # Headers
        if queryset.exists():
            model = queryset.model
            fields = [f.name for f in model._meta.fields]
            writer.writerow(fields)
            
            # Data
            for obj in queryset:
                row = [getattr(obj, field, '') for field in fields]
                writer.writerow(row)
        
        return response

class WebsiteScopedViewSetMixin:
    """
    Mixin pour ViewSets scopés par website
    
    Filtre par websites de brands accessibles
    """
    
    def get_queryset(self):
        """Filtre par websites des brands accessibles"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.none()
        
        # Company admin : accès total
        if hasattr(user, 'is_company_admin') and user.is_company_admin():
            return queryset
        
        # Filtrage par websites des brands accessibles
        if hasattr(user, 'brands'):
            accessible_brands = user.brands.all()
            return queryset.filter(website__brand__in=accessible_brands)
        
        return queryset.none()

class SoftDeleteViewSetMixin:
    """
    Mixin pour gestion suppression logique
    
    Override destroy pour soft delete
    """
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete au lieu de suppression physique"""
        instance = self.get_object()
        
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        POST /items/{id}/restore/
        
        Restaure un élément supprimé logiquement
        """
        instance = self.get_object()
        
        if hasattr(instance, 'restore'):
            instance.restore()
            return Response({
                'message': 'Élément restauré avec succès',
                'item': self.get_serializer(instance).data
            })
        else:
            return Response(
                {'error': 'Restauration non supportée'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UserOwnedViewSetMixin:
    """
    Mixin pour ViewSets avec propriétaire
    
    Assigne automatiquement created_by/updated_by
    """
    
    def perform_create(self, serializer):
        """Assigne created_by automatiquement"""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Assigne updated_by automatiquement"""
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            super().perform_update(serializer)