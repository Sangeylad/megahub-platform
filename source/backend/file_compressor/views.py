# backend/file_compressor/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.files.storage import default_storage
from django.db import models
from datetime import timedelta
import os

# Import uniquement les modèles qui existent
from .models import SupportedFileType, FileOptimization, OptimizationQuota
from .serializers.compression_serializers import (
    SupportedFileTypeSerializer, 
    FileOptimizationSerializer,
    OptimizationQuotaSerializer,
    FileOptimizationCreateSerializer
)
from .services.file_optimization_service import FileOptimizationService
from .tasks import optimize_file_task

class SupportedFileTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de fichiers supportés pour l'optimisation"""
    queryset = SupportedFileType.objects.filter(is_active=True)
    serializer_class = SupportedFileTypeSerializer
    permission_classes = [IsAuthenticated]

class FileOptimizationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les optimisations de fichiers (réduction de taille)"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FileOptimizationCreateSerializer
        return FileOptimizationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'current_brand') and user.current_brand:
            return FileOptimization.objects.filter(
                brand=user.current_brand,
                user=user
            ).select_related('file_type', 'brand').order_by('-created_at')
        return FileOptimization.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle optimisation"""
        try:
            user = request.user
            if not hasattr(user, 'current_brand') or not user.current_brand:
                return Response({'error': 'Aucune brand sélectionnée'}, status=400)
            
            brand = user.current_brand
            
            # Vérification des quotas
            quota, created = OptimizationQuota.objects.get_or_create(
                brand=brand,
                defaults={'reset_date': timezone.now() + timedelta(days=30)}
            )
            
            # Reset automatique si nécessaire
            if timezone.now() > quota.reset_date:
                quota.current_month_usage = 0
                quota.reset_date = timezone.now() + timedelta(days=30)
                quota.save()
            
            # Validation du fichier uploadé
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({'error': 'Aucun fichier fourni'}, status=400)
            
            # Vérification quota
            can_optimize, error_msg = quota.can_optimize(file_size=uploaded_file.size)
            if not can_optimize:
                return Response({'error': error_msg}, status=400)
            
            # Sauvegarde temporaire du fichier
            upload_path = f"uploads/optimizations/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            saved_path = default_storage.save(upload_path, uploaded_file)
            
            # Création via le service
            service = FileOptimizationService()
            file_data = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'mime_type': uploaded_file.content_type,
                'storage_path': saved_path
            }
            
            optimization = service.create_optimization_job(
                user=user,
                brand=brand,
                file_data=file_data,
                quality_level=request.data.get('quality_level', 'medium'),
                resize_enabled=request.data.get('resize_enabled', False),
                target_width=request.data.get('target_width'),
                target_height=request.data.get('target_height')
            )
            
            # Incrément du quota
            quota.increment_usage()
            
            # Lancement de la tâche d'optimisation
            task = optimize_file_task.delay(str(optimization.id))
            optimization.task_id = task.id
            optimization.save()
            
            serializer = self.get_serializer(optimization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger le fichier optimisé"""
        optimization = self.get_object()
        
        if optimization.status != 'completed':
            return Response({'error': 'Optimisation non terminée'}, status=400)
        
        if optimization.expires_at and timezone.now() > optimization.expires_at:
            return Response({'error': 'Fichier expiré'}, status=410)
        
        if not optimization.download_url:
            return Response({'error': 'Fichier non disponible'}, status=404)
        
        return Response({
            'download_url': optimization.download_url,
            'filename': optimization.optimized_filename,
            'size': optimization.optimized_size
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques d'optimisation pour la brand"""
        user = request.user
        if not hasattr(user, 'current_brand') or not user.current_brand:
            return Response({'error': 'Aucune brand sélectionnée'}, status=400)
        
        service = FileOptimizationService()
        stats = service.get_optimization_stats(user.current_brand.id)
        
        return Response(stats)

class OptimizationQuotaView(APIView):
    """Vue pour consulter les quotas d'optimisation"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'current_brand') or not user.current_brand:
            return Response({'error': 'Aucune brand sélectionnée'}, status=400)
        
        quota, created = OptimizationQuota.objects.get_or_create(
            brand=user.current_brand,
            defaults={'reset_date': timezone.now() + timedelta(days=30)}
        )
        
        # Reset automatique si nécessaire
        if timezone.now() > quota.reset_date:
            quota.current_month_usage = 0
            quota.reset_date = timezone.now() + timedelta(days=30)
            quota.save()
        
        serializer = OptimizationQuotaSerializer(quota)
        return Response(serializer.data)

class OptimizationStatsView(APIView):
    """Vue pour les statistiques d'optimisation"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'current_brand') or not user.current_brand:
            return Response({'error': 'Aucune brand sélectionnée'}, status=400)
        
        service = FileOptimizationService()
        stats = service.get_optimization_stats(user.current_brand.id)
        
        # Statistiques par type de fichier
        file_type_stats = FileOptimization.objects.filter(
            brand=user.current_brand,
            status='completed'
        ).values('file_type__category', 'file_type__name').annotate(
            count=models.Count('id'),
            avg_reduction=models.Avg('size_reduction_percentage'),
            total_saved=models.Sum('size_reduction_bytes')
        ).order_by('-count')
        
        stats['by_file_type'] = list(file_type_stats)
        
        return Response(stats)