# backend/file_compressor/services/file_optimization_service.py
import os
import io
import tempfile
import shutil
from PIL import Image
import fitz  # PyMuPDF pour PDF
from typing import Tuple, Dict, Any
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import models
import logging

from ..models import FileOptimization, SupportedFileType

logger = logging.getLogger(__name__)

class FileOptimizationService:
    """Service d'optimisation de fichiers (réduction de taille) pour utilisateurs authentifiés"""
    
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', 'optimization')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.quality_mapping = {
            'low': 40,      # Compression maximale
            'medium': 70,   # Équilibre qualité/taille
            'high': 85,     # Haute qualité
            'lossless': 95  # Quasi sans perte
        }
        
        self.supported_types = {
            'image/jpeg': self._optimize_jpeg,
            'image/jpg': self._optimize_jpeg,
            'image/png': self._optimize_png,
            'image/webp': self._optimize_webp,
            'application/pdf': self._optimize_pdf,
        }
    
    def can_optimize(self, mime_type: str) -> bool:
        """Vérifie si le type de fichier est supporté pour l'optimisation"""
        return mime_type.lower() in self.supported_types
    
    def create_optimization_job(self, user, brand, file_data: Dict, 
                               quality_level: str = 'medium',
                               resize_enabled: bool = False,
                               target_width: int = None,
                               target_height: int = None) -> FileOptimization:
        """Crée un job d'optimisation de fichier"""
        try:
            # Validation du type de fichier
            mime_type = file_data.get('mime_type')
            if not self.can_optimize(mime_type):
                raise ValueError(f"Type de fichier non supporté pour l'optimisation: {mime_type}")
            
            # Récupération du type supporté
            file_type = SupportedFileType.objects.filter(
                mime_type=mime_type,
                is_active=True
            ).first()
            
            if not file_type:
                raise ValueError(f"Configuration manquante pour: {mime_type}")
            
            # Création du job
            optimization = FileOptimization.objects.create(
                user=user,
                brand=brand,
                original_filename=file_data['name'],
                original_size=file_data['size'],
                original_mime_type=mime_type,
                file_type=file_type,
                quality_level=quality_level,
                resize_enabled=resize_enabled,
                target_width=target_width,
                target_height=target_height,
                status='pending'
            )
            
            logger.info(f"Job optimisation créé: {optimization.id} ({file_data['name']})")
            return optimization
            
        except Exception as e:
            logger.error(f"Erreur création job optimisation: {str(e)}")
            raise
    
    def perform_optimization(self, optimization_id: str) -> bool:
        """Effectue l'optimisation (appelé par tâche Celery)"""
        try:
            optimization = FileOptimization.objects.get(id=optimization_id)
            optimization.status = 'processing'
            optimization.save()
            
            logger.info(f"Début optimisation {optimization_id}")
            start_time = timezone.now()
            
            # Création du dossier temporaire
            temp_job_dir = os.path.join(self.temp_dir, str(optimization_id))
            os.makedirs(temp_job_dir, exist_ok=True)
            
            try:
                # Téléchargement du fichier source
                source_path = self._download_source_file(optimization, temp_job_dir)
                
                # Optimisation selon le type
                optimized_path = self._optimize_file(optimization, source_path, temp_job_dir)
                
                # Upload du fichier optimisé
                download_url = self._upload_optimized_file(optimization, optimized_path)
                
                # Mise à jour du job
                optimized_size = os.path.getsize(optimized_path)
                optimization_time = (timezone.now() - start_time).total_seconds()
                
                optimization.status = 'completed'
                optimization.completed_at = timezone.now()
                optimization.optimized_size = optimized_size
                optimization.optimization_time = optimization_time
                optimization.download_url = download_url
                optimization.save()
                
                logger.info(f"Optimisation {optimization_id} terminée: {optimized_size} bytes")
                return True
                
            finally:
                # Nettoyage
                if os.path.exists(temp_job_dir):
                    shutil.rmtree(temp_job_dir)
                    
        except FileOptimization.DoesNotExist:
            logger.error(f"Optimisation {optimization_id} non trouvée")
            return False
        except Exception as e:
            logger.error(f"Erreur optimisation {optimization_id}: {str(e)}")
            self._mark_as_failed(optimization_id, str(e))
            return False
    
    def _download_source_file(self, optimization: FileOptimization, temp_dir: str) -> str:
        """Télécharge le fichier source depuis le storage"""
        source_path_in_storage = f"uploads/optimizations/{optimization.id}/{optimization.original_filename}"
        temp_file_path = os.path.join(temp_dir, optimization.original_filename)
        
        if default_storage.exists(source_path_in_storage):
            with default_storage.open(source_path_in_storage, 'rb') as source_file:
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(source_file.read())
            return temp_file_path
        else:
            raise Exception(f"Fichier source non trouvé: {source_path_in_storage}")
    
    def _optimize_file(self, optimization: FileOptimization, source_path: str, temp_dir: str) -> str:
        """Effectue l'optimisation selon le type MIME"""
        mime_type = optimization.original_mime_type.lower()
        
        if mime_type not in self.supported_types:
            raise ValueError(f"Type MIME non supporté: {mime_type}")
        
        optimizer = self.supported_types[mime_type]
        return optimizer(optimization, source_path, temp_dir)
    
    def _optimize_jpeg(self, optimization: FileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation JPEG avec réduction de qualité et redimensionnement"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_path = os.path.join(temp_dir, f"{base_name}_optimized.jpg")
        
        try:
            quality = self.quality_mapping.get(optimization.quality_level, 70)
            
            with Image.open(source_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                
                # Redimensionnement si demandé
                if optimization.resize_enabled:
                    target_width = optimization.target_width
                    target_height = optimization.target_height
                    
                    if target_width or target_height:
                        if optimization.maintain_aspect_ratio:
                            # Calcul proportionnel
                            if target_width and target_height:
                                img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                            elif target_width:
                                ratio = target_width / original_width
                                new_height = int(original_height * ratio)
                                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                            elif target_height:
                                ratio = target_height / original_height
                                new_width = int(original_width * ratio)
                                img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                        else:
                            # Redimensionnement exact
                            img = img.resize((target_width or original_width, 
                                            target_height or original_height), 
                                           Image.Resampling.LANCZOS)
                
                # Réduction automatique si très grande image
                max_dimension = 2048 if optimization.quality_level == 'high' else 1600
                if max(img.size) > max_dimension and not optimization.resize_enabled:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Sauvegarde avec compression
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                # Mise à jour des métadonnées
                optimization.final_dimensions = {"width": img.width, "height": img.height}
                optimization.final_quality = quality
                optimization.save()
            
            optimization.optimized_filename = f"{base_name}_optimized.jpg"
            optimization.save()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur optimisation JPEG: {str(e)}")
            raise
    
    def _optimize_png(self, optimization: FileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation PNG avec réduction de couleurs et redimensionnement"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_path = os.path.join(temp_dir, f"{base_name}_optimized.png")
        
        try:
            with Image.open(source_path) as img:
                original_width, original_height = img.size
                
                # Redimensionnement si demandé (même logique que JPEG)
                if optimization.resize_enabled:
                    target_width = optimization.target_width
                    target_height = optimization.target_height
                    
                    if target_width or target_height:
                        if optimization.maintain_aspect_ratio:
                            if target_width and target_height:
                                img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                            elif target_width:
                                ratio = target_width / original_width
                                new_height = int(original_height * ratio)
                                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                            elif target_height:
                                ratio = target_height / original_height
                                new_width = int(original_width * ratio)
                                img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                        else:
                            img = img.resize((target_width or original_width, 
                                            target_height or original_height), 
                                           Image.Resampling.LANCZOS)
                
                # Réduction automatique si très grande
                max_dimension = 2048 if optimization.quality_level == 'high' else 1600
                if max(img.size) > max_dimension and not optimization.resize_enabled:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Réduction du nombre de couleurs selon la qualité
                if optimization.quality_level == 'low':
                    # Conversion en palette pour réduire drastiquement
                    if img.mode == 'RGBA':
                        img = img.quantize(colors=32, method=Image.Quantize.MEDIANCUT)
                    else:
                        img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=32)
                elif optimization.quality_level == 'medium':
                    if img.mode == 'RGBA':
                        img = img.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
                    else:
                        img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=128)
                # 'high' et 'lossless' gardent la qualité originale
                
                # Sauvegarde optimisée
                img.save(output_path, 'PNG', optimize=True)
                
                # Mise à jour des métadonnées
                optimization.final_dimensions = {"width": img.width, "height": img.height}
                optimization.save()
            
            optimization.optimized_filename = f"{base_name}_optimized.png"
            optimization.save()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur optimisation PNG: {str(e)}")
            raise
    
    def _optimize_webp(self, optimization: FileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation WebP (très efficace)"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_path = os.path.join(temp_dir, f"{base_name}_optimized.webp")
        
        try:
            quality = self.quality_mapping.get(optimization.quality_level, 70)
            
            with Image.open(source_path) as img:
                original_width, original_height = img.size
                
                # Redimensionnement si demandé (même logique que JPEG)
                if optimization.resize_enabled:
                    target_width = optimization.target_width
                    target_height = optimization.target_height
                    
                    if target_width or target_height:
                        if optimization.maintain_aspect_ratio:
                            if target_width and target_height:
                                img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                            elif target_width:
                                ratio = target_width / original_width
                                new_height = int(original_height * ratio)
                                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                            elif target_height:
                                ratio = target_height / original_height
                                new_width = int(original_width * ratio)
                                img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                
                # Réduction automatique si très grande
                max_dimension = 2048 if optimization.quality_level == 'high' else 1600
                if max(img.size) > max_dimension and not optimization.resize_enabled:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # WebP supporte nativement la transparence
                lossless = optimization.quality_level == 'lossless'
                
                if lossless:
                    img.save(output_path, 'WebP', lossless=True, optimize=True)
                else:
                    img.save(output_path, 'WebP', quality=quality, optimize=True)
                
                # Mise à jour des métadonnées
                optimization.final_dimensions = {"width": img.width, "height": img.height}
                optimization.final_quality = quality if not lossless else 100
                optimization.save()
            
            optimization.optimized_filename = f"{base_name}_optimized.webp"
            optimization.save()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur optimisation WebP: {str(e)}")
            raise
    
    def _optimize_pdf(self, optimization: FileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation PDF avec PyMuPDF"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_path = os.path.join(temp_dir, f"{base_name}_optimized.pdf")
        
        try:
            # Mapping des niveaux de compression
            compression_settings = {
                'low': {
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'garbage': 3,
                    'clean': True,
                    'ascii': True,
                    'linear': True,
                    'image_quality': 30
                },
                'medium': {
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'garbage': 2,
                    'clean': True,
                    'ascii': True,
                    'image_quality': 60
                },
                'high': {
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'garbage': 1,
                    'clean': True,
                    'image_quality': 80
                },
                'lossless': {
                    'deflate': True,
                    'deflate_fonts': True,
                    'garbage': 1,
                    'clean': True
                }
            }
            
            settings = compression_settings.get(optimization.quality_level, compression_settings['medium'])
            
            # Ouverture et traitement du PDF
            pdf_document = fitz.open(source_path)
            
            # Compression des images dans le PDF (sauf lossless)
            if optimization.quality_level != 'lossless':
                image_quality = settings.get('image_quality', 60)
                
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            base_image = pdf_document.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Compression si image > 100KB
                            if len(image_bytes) > 100000:
                                image = Image.open(io.BytesIO(image_bytes))
                                
                                # Redimensionnement si trop grande
                                max_size = 1024 if optimization.quality_level == 'low' else 1536
                                if max(image.size) > max_size:
                                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                                
                                # Compression selon format
                                output_buffer = io.BytesIO()
                                if image.mode in ('RGBA', 'LA'):
                                    image.save(output_buffer, 'PNG', optimize=True)
                                else:
                                    image.save(output_buffer, 'JPEG', quality=image_quality, optimize=True)
                                
                                # Remplacement dans le PDF si gain de place
                                compressed_image = output_buffer.getvalue()
                                if len(compressed_image) < len(image_bytes):
                                    pdf_document.update_stream(xref, compressed_image)
                        
                        except Exception as img_error:
                            logger.warning(f"Impossible de compresser l'image {img_index}: {str(img_error)}")
                            continue
            
            # Sauvegarde avec options de compression
            pdf_document.save(output_path, **{k: v for k, v in settings.items() if k != 'image_quality'})
            pdf_document.close()
            
            optimization.optimized_filename = f"{base_name}_optimized.pdf"
            optimization.save()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur optimisation PDF: {str(e)}")
            raise
    
    def _upload_optimized_file(self, optimization: FileOptimization, optimized_path: str) -> str:
        """Upload le fichier optimisé vers le storage"""
        filename = optimization.optimized_filename
        storage_path = f"optimizations/{optimization.brand.id}/{optimization.id}/{filename}"
        
        with open(optimized_path, 'rb') as optimized_file:
            saved_path = default_storage.save(storage_path, optimized_file)
        
        return default_storage.url(saved_path)
    
    def _mark_as_failed(self, optimization_id: str, error_message: str):
        """Marque une optimisation comme échouée"""
        try:
            optimization = FileOptimization.objects.get(id=optimization_id)
            optimization.status = 'failed'
            optimization.error_message = error_message[:500]
            optimization.save()
        except FileOptimization.DoesNotExist:
            pass
    
    def get_optimization_stats(self, brand_id: int) -> Dict[str, Any]:
        """Statistiques d'optimisation pour une brand"""
        optimizations = FileOptimization.objects.filter(brand_id=brand_id)
        
        total_optimizations = optimizations.count()
        successful_optimizations = optimizations.filter(status='completed').count()
        
        if successful_optimizations > 0:
            avg_reduction = optimizations.filter(
                status='completed',
                size_reduction_percentage__isnull=False
            ).aggregate(
                avg_reduction=models.Avg('size_reduction_percentage')
            )['avg_reduction'] or 0
            
            total_saved_bytes = optimizations.filter(
                status='completed'
            ).aggregate(
                total_saved=models.Sum('size_reduction_bytes')
            )['total_saved'] or 0
        else:
            avg_reduction = 0
            total_saved_bytes = 0
        
        return {
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'success_rate': successful_optimizations / total_optimizations if total_optimizations > 0 else 0,
            'average_size_reduction': avg_reduction,
            'total_space_saved_bytes': total_saved_bytes,
            'total_space_saved_mb': total_saved_bytes / (1024 * 1024) if total_saved_bytes > 0 else 0
        }