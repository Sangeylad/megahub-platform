# backend/file_converter/views.py

import logging
from django.http import HttpResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import FileConversion, SupportedFormat, ConversionQuota
from .serializers import (
    FileConversionSerializer, ConversionCreateSerializer,
    SupportedFormatSerializer, ConversionQuotaSerializer
)
from .services.conversion_service import ConversionService
from .services.download_service import DownloadService
from .services.quota_service import QuotaService
from .tasks import convert_file_task
from .utils import get_user_brands, get_default_brand_for_user

logger = logging.getLogger(__name__)

class SupportedFormatViewSet(viewsets.ReadOnlyModelViewSet):
    """Formats supportés (lecture seule)"""
    queryset = SupportedFormat.objects.all()
    serializer_class = SupportedFormatSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Retourne les formats groupés par catégorie"""
        service = ConversionService()
        formats = service.get_supported_formats()
        return Response(formats)
    
    @action(detail=False, methods=['get'])
    def conversions(self, request):
        """Retourne les conversions possibles pour un format d'entrée"""
        input_format = request.query_params.get('input')
        if not input_format:
            return Response(
                {'error': 'Paramètre input requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ConversionService()
        possible_outputs = []
        
        for output_format in SupportedFormat.objects.filter(is_output=True):
            can_convert, _ = service.can_convert(input_format, output_format.name)
            if can_convert:
                possible_outputs.append({
                    'name': output_format.name,
                    'mime_type': output_format.mime_type,
                    'category': output_format.category
                })
        
        return Response({
            'input_format': input_format,
            'possible_outputs': possible_outputs
        })


class FileConversionViewSet(viewsets.ModelViewSet):
    """Gestion des conversions de fichiers"""
    serializer_class = FileConversionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'input_format__name', 'output_format__name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtre par brands accessibles à l'utilisateur"""
        user_brands = get_user_brands(self.request.user)
        return FileConversion.objects.filter(
            brand__in=user_brands
        ).select_related(
            'input_format', 'output_format', 'user', 'brand'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversionCreateSerializer
        return FileConversionSerializer
    
    def create(self, request, *args, **kwargs):
        """Démarre une nouvelle conversion"""
        try:
            # Validation et récupération de la brand
            brand = self._get_brand_from_request(request)
            
            # Validation du serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Vérification du quota
            quota_service = QuotaService()
            file_obj = serializer.validated_data['file']
            can_convert, error_msg = quota_service.check_quota(brand, file_obj.size)
            if not can_convert:
                return Response(
                    {'error': error_msg}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Création de la conversion
            conversion_service = ConversionService()
            conversion = conversion_service.create_conversion(
                user=request.user,
                brand=brand,
                file_obj=file_obj,
                output_format=serializer.validated_data['output_format'],
                options=serializer.validated_data.get('options', {})
            )
            
            # Lancement de la tâche asynchrone
            task = convert_file_task.delay(conversion.id)
            conversion.task_id = task.id
            conversion.save(update_fields=['task_id'])
            
            response_serializer = FileConversionSerializer(conversion)
            
            logger.info(f"Conversion {conversion.id} créée et tâche {task.id} lancée")
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur création conversion: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erreur serveur lors de la création'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharge le fichier converti"""
        try:
            conversion = self.get_object()
            download_service = DownloadService()
            
            return download_service.download_conversion(conversion, request.user)
            
        except PermissionError:
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http404:
            return Response(
                {'error': 'Fichier non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erreur téléchargement conversion {pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erreur téléchargement'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        """Annule une conversion en cours"""
        try:
            conversion = self.get_object()
            
            if conversion.status not in ['pending', 'processing']:
                return Response(
                    {'error': 'Impossible d\'annuler cette conversion'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Révoquer la tâche Celery
            self._cancel_celery_task(conversion.task_id)
            
            # Supprimer la conversion
            conversion.delete()
            
            logger.info(f"Conversion {pk} annulée par utilisateur {request.user.id}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"Erreur annulation conversion {pk}: {str(e)}")
            return Response(
                {'error': 'Erreur lors de l\'annulation'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def quota(self, request):
        """Retourne les informations de quota"""
        try:
            brand = self._get_brand_from_request(request, required=False)
            if not brand:
                return Response(
                    {'error': 'Aucune brand accessible'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            quota_service = QuotaService()
            quota = quota_service.get_or_create_quota(brand)
            
            serializer = ConversionQuotaSerializer(quota)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Erreur récupération quota: {str(e)}")
            return Response(
                {'error': 'Erreur récupération quota'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques de conversion"""
        try:
            brand = self._get_brand_from_request(request, required=False)
            if not brand:
                return Response(
                    {'error': 'Aucune brand accessible'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversion_service = ConversionService()
            stats = conversion_service.get_conversion_statistics(brand)
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Erreur récupération stats: {str(e)}")
            return Response(
                {'error': 'Erreur récupération statistiques'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_brand_from_request(self, request, required=True):
        """Récupère la brand depuis les paramètres ou par défaut"""
        brand_id = request.data.get('brand_id') or request.query_params.get('brand_id')
        
        if brand_id:
            try:
                user_brands = get_user_brands(request.user)
                return user_brands.get(id=brand_id)
            except Exception:
                if required:
                    raise ValueError('Brand non trouvée ou accès refusé')
                return None
        else:
            brand = get_default_brand_for_user(request.user)
            if not brand and required:
                raise ValueError('Aucune brand accessible')
            return brand
    
    def _cancel_celery_task(self, task_id):
        """Annule une tâche Celery"""
        if task_id:
            try:
                from celery import current_app
                current_app.control.revoke(task_id, terminate=True)
            except Exception as e:
                logger.warning(f"Impossible d'annuler la tâche Celery {task_id}: {str(e)}")