# backend/public_tools/services/public_optimization_service.py
import os
import tempfile
import shutil
from PIL import Image
import fitz
from typing import Dict, Any, Tuple
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
import logging

from ..models import PublicFileOptimization, PublicOptimizationQuota

logger = logging.getLogger(__name__)

class PublicOptimizationService:
    """Service d'optimisation pour les utilisateurs publics (réduction de taille)"""
    
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', 'public_optimization')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.quality_mapping = {
            'low': 35,      # Compression maximale pour public
            'medium': 65,   # Équilibre
            'high': 80,     # Bonne qualité
        }
        
        self.supported_extensions = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
        }
    
    def validate_optimization_request(self, ip_address: str, file_data: Dict) -> Tuple[bool, str]:
        """Valide une demande d'optimisation publique"""
        try:
            # Vérification des quotas
            quota, created = PublicOptimizationQuota.objects.get_or_create(
                ip_address=ip_address
            )
            
            file_size = file_data.get('size', 0)
            can_optimize, error_message = quota.can_optimize(file_size=file_size)
            
            if not can_optimize:
                return False, error_message
            
            # Validation du fichier
            filename = file_data.get('name', '')
            if not filename or len(filename) > 255:
                return False, "Nom de fichier invalide"
            
            # Extension supportée
            file_extension = os.path.splitext(filename.lower())[1]
            if file_extension not in self.supported_extensions:
                supported = ', '.join(self.supported_extensions.keys())
                return False, f"Type de fichier non supporté. Formats acceptés: {supported}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Erreur validation optimisation publique: {str(e)}")
            return False, "Erreur de validation"
    
    def create_public_optimization(self, ip_address: str, user_agent: str,
                                 file_data: Dict, quality_level: str = 'medium',
                                 resize_enabled: bool = False,
                                 target_max_dimension: int = None) -> PublicFileOptimization:
        """Crée une optimisation publique"""
        try:
            filename = file_data['name']
            file_extension = os.path.splitext(filename.lower())[1]
            mime_type = self.supported_extensions[file_extension]
            
            optimization = PublicFileOptimization.objects.create(
                ip_address=ip_address,
                user_agent=user_agent[:500],
                original_filename=filename,
                original_size=file_data['size'],
                original_mime_type=mime_type,
                file_extension=file_extension,
                quality_level=quality_level,
                resize_enabled=resize_enabled,
                target_max_dimension=target_max_dimension,
                status='pending'
            )
            
            # Incrément du quota
            quota = PublicOptimizationQuota.objects.get(ip_address=ip_address)
            quota.increment_usage()
            
            logger.info(f"Optimisation publique créée: {optimization.id} de {ip_address}")
            return optimization
            
        except Exception as e:
            logger.error(f"Erreur création optimisation publique: {str(e)}")
            raise
    
    def perform_public_optimization(self, optimization_id: str) -> bool:
        """Effectue l'optimisation publique"""
        try:
            optimization = PublicFileOptimization.objects.get(id=optimization_id)
            optimization.status = 'processing'
            optimization.save()
            
            logger.info(f"Début optimisation publique {optimization_id}")
            start_time = timezone.now()
            
            # Dossier temporaire
            temp_job_dir = os.path.join(self.temp_dir, str(optimization_id))
            os.makedirs(temp_job_dir, exist_ok=True)
            
            try:
                # Récupération du fichier source
                source_path = self._prepare_source_file(optimization, temp_job_dir)
                
                if not source_path:
                    raise Exception("Fichier source non trouvé")
                
                # Optimisation selon le type
                optimized_path = self._optimize_public_file(optimization, source_path, temp_job_dir)
                
                # Upload vers storage public
                self._upload_public_optimized_file(optimization, optimized_path)
                
                # Finalisation
                optimized_size = os.path.getsize(optimized_path)
                optimization_time = (timezone.now() - start_time).total_seconds()
                
                optimization.status = 'completed'
                optimization.completed_at = timezone.now()
                optimization.optimized_size = optimized_size
                optimization.optimization_time = optimization_time
                optimization.save()
                
                logger.info(f"Optimisation publique {optimization_id} terminée")
                return True
                
            finally:
                # Nettoyage immédiat
                if os.path.exists(temp_job_dir):
                    shutil.rmtree(temp_job_dir)
                    
        except PublicFileOptimization.DoesNotExist:
            logger.error(f"Optimisation publique {optimization_id} non trouvée")
            return False
        except Exception as e:
            logger.error(f"Erreur optimisation publique {optimization_id}: {str(e)}")
            self._mark_public_as_failed(optimization_id, str(e))
            return False
    
    def _prepare_source_file(self, optimization: PublicFileOptimization, temp_dir: str) -> str:
        """Prépare le fichier source pour optimisation publique"""
        # Le fichier est supposé être dans un dossier temporaire d'upload
        temp_upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp', 'uploads', str(optimization.id))
        source_file_path = os.path.join(temp_upload_dir, optimization.original_filename)
        
        if os.path.exists(source_file_path):
            # Copie vers le dossier de traitement
            dest_path = os.path.join(temp_dir, optimization.original_filename)
            shutil.copy2(source_file_path, dest_path)
            return dest_path
        else:
            logger.warning(f"Fichier source non trouvé: {source_file_path}")
            return None
    
    def _optimize_public_file(self, optimization: PublicFileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimise un fichier pour usage public"""
        mime_type = optimization.original_mime_type.lower()
        
        if mime_type in ['image/jpeg', 'image/jpg']:
            return self._optimize_public_jpeg(optimization, source_path, temp_dir)
        elif mime_type == 'image/png':
            return self._optimize_public_png(optimization, source_path, temp_dir)
        elif mime_type == 'image/webp':
            return self._optimize_public_webp(optimization, source_path, temp_dir)
        elif mime_type == 'application/pdf':
            return self._optimize_public_pdf(optimization, source_path, temp_dir)
        else:
            raise ValueError(f"Type MIME non supporté: {mime_type}")
    
    def _optimize_public_jpeg(self, optimization: PublicFileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation JPEG publique"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_filename = f"{base_name}_optimized.jpg"
        output_path = os.path.join(temp_dir, output_filename)
        
        quality = self.quality_mapping.get(optimization.quality_level, 65)
        
        with Image.open(source_path) as img:
            # Conversion en RGB si nécessaire
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionnement si demandé
            if optimization.resize_enabled and optimization.target_max_dimension:
                max_dim = optimization.target_max_dimension
                if max(img.size) > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            # Réduction automatique pour public (plus aggressive)
            max_public_dimension = min(optimization.target_max_dimension or 1536, 1536)
            if max(img.size) > max_public_dimension:
                img.thumbnail((max_public_dimension, max_public_dimension), Image.Resampling.LANCZOS)
            
            # Sauvegarde avec compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        optimization.optimized_filename = output_filename
        optimization.save()
        
        return output_path
    
    def _optimize_public_png(self, optimization: PublicFileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation PNG publique"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_filename = f"{base_name}_optimized.png"
        output_path = os.path.join(temp_dir, output_filename)
        
        with Image.open(source_path) as img:
            # Redimensionnement
            if optimization.resize_enabled and optimization.target_max_dimension:
                max_dim = optimization.target_max_dimension
                if max(img.size) > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            # Réduction automatique pour public
            max_public_dimension = min(optimization.target_max_dimension or 1536, 1536)
            if max(img.size) > max_public_dimension:
                img.thumbnail((max_public_dimension, max_public_dimension), Image.Resampling.LANCZOS)
            
            # Réduction des couleurs pour compression
            if optimization.quality_level == 'low':
                if img.mode == 'RGBA':
                    img = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
                else:
                    img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=64)
            elif optimization.quality_level == 'medium':
                if img.mode == 'RGBA':
                    img = img.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
                else:
                    img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=128)
            
            # Sauvegarde optimisée
            img.save(output_path, 'PNG', optimize=True)
        
        optimization.optimized_filename = output_filename
        optimization.save()
        
        return output_path
    
    def _optimize_public_webp(self, optimization: PublicFileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation WebP publique"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_filename = f"{base_name}_optimized.webp"
        output_path = os.path.join(temp_dir, output_filename)
        
        quality = self.quality_mapping.get(optimization.quality_level, 65)
        
        with Image.open(source_path) as img:
            # Redimensionnement
            if optimization.resize_enabled and optimization.target_max_dimension:
                max_dim = optimization.target_max_dimension
                if max(img.size) > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            # Réduction automatique pour public
            max_public_dimension = min(optimization.target_max_dimension or 1536, 1536)
            if max(img.size) > max_public_dimension:
                img.thumbnail((max_public_dimension, max_public_dimension), Image.Resampling.LANCZOS)
            
            # WebP avec compression
            img.save(output_path, 'WebP', quality=quality, optimize=True)
        
        optimization.optimized_filename = output_filename
        optimization.save()
        
        return output_path
    
    def _optimize_public_pdf(self, optimization: PublicFileOptimization, source_path: str, temp_dir: str) -> str:
        """Optimisation PDF publique (simple)"""
        base_name = os.path.splitext(optimization.original_filename)[0]
        output_filename = f"{base_name}_optimized.pdf"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Configuration simple pour public
        pdf_settings = {
            'deflate': True,
            'deflate_images': True,
            'deflate_fonts': True,
            'garbage': 2,
            'clean': True
        }
        
        # Ouverture et compression basique
        pdf_document = fitz.open(source_path)
        pdf_document.save(output_path, **pdf_settings)
        pdf_document.close()
        
        optimization.optimized_filename = output_filename
        optimization.save()
        
        return output_path
    
    def _upload_public_optimized_file(self, optimization: PublicFileOptimization, optimized_path: str):
        """Upload le fichier optimisé vers storage public"""
        filename = optimization.optimized_filename
        storage_path = f"public_optimizations/{optimization.id}/{filename}"
        
        with open(optimized_path, 'rb') as optimized_file:
            saved_path = default_storage.save(storage_path, optimized_file)
        
        return saved_path
    
    def _mark_public_as_failed(self, optimization_id: str, error_message: str):
        """Marque une optimisation publique comme échouée"""
        try:
            optimization = PublicFileOptimization.objects.get(id=optimization_id)
            optimization.status = 'failed'
            optimization.error_message = error_message[:500]
            optimization.save()
        except PublicFileOptimization.DoesNotExist:
            pass
    
    def cleanup_expired_files(self) -> Dict[str, Any]:
        """Nettoyage des optimisations publiques expirées"""
        try:
            expired_optimizations = PublicFileOptimization.objects.filter(
                expires_at__lt=timezone.now()
            )
            
            deleted_files = 0
            for optimization in expired_optimizations:
                # Suppression du fichier de storage
                if optimization.optimized_filename:
                    storage_path = f"public_optimizations/{optimization.id}/{optimization.optimized_filename}"
                    if default_storage.exists(storage_path):
                        default_storage.delete(storage_path)
                        deleted_files += 1
                
                # Suppression des fichiers temporaires d'upload
                temp_upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp', 'uploads', str(optimization.id))
                if os.path.exists(temp_upload_dir):
                    shutil.rmtree(temp_upload_dir)
            
            # Suppression des enregistrements
            deleted_count = expired_optimizations.delete()[0]
            
            return {
                'deleted_optimizations': deleted_count,
                'deleted_files': deleted_files,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Erreur nettoyage optimisations publiques: {str(e)}")
            return {'error': str(e)}