# backend/file_compressor/services/compression_service.py
import os
import zipfile
import tempfile
import shutil
from typing import List, Dict, Any, Tuple
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import models
import logging

logger = logging.getLogger(__name__)

class CompressionService:
    """Service de compression pour créer des archives (ZIP) - Version simplifiée"""
    
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', 'compression')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Formats supportés en dur pour l'instant
        self.supported_formats = {
            'zip': {
                'extension': '.zip',
                'mime_type': 'application/zip',
                'compression_levels': {
                    'fastest': 1,
                    'normal': 6,
                    'maximum': 9
                }
            }
        }
    
    def create_compression_job(self, user, brand, files_data: List[Dict],
                              output_format: str = 'zip', compression_level: str = 'normal',
                             password: str = None, split_size: int = None) -> Dict[str, Any]:
        """Crée un job de compression d'archive (version simplifiée sans modèle)"""
        try:
            # Validation du format
            if output_format not in self.supported_formats:
                raise ValueError(f"Format non supporté: {output_format}")
            
            # Calcul taille totale
            total_size = sum(file_data.get('size', 0) for file_data in files_data)
            
            # Génération d'un ID temporaire
            import uuid
            compression_id = str(uuid.uuid4())
            
            # Création des informations de compression
            compression_info = {
                'id': compression_id,
                'user_id': user.id,
                'brand_id': brand.id,
                'source_files_info': files_data,
                'total_source_size': total_size,
                'files_count': len(files_data),
                'output_format': output_format,
                'compression_level': compression_level,
                'password_protected': bool(password),
                'split_archive': bool(split_size),
                'split_size': split_size,
                'status': 'pending',
                'created_at': timezone.now().isoformat()
            }
            
            logger.info(f"Job compression créé: {compression_id} ({len(files_data)} fichiers)")
            return compression_info
            
        except Exception as e:
            logger.error(f"Erreur création job compression: {str(e)}")
            raise
    
    def perform_compression(self, compression_info: Dict[str, Any]) -> bool:
        """Effectue la compression d'archive"""
        try:
            compression_id = compression_info['id']
            logger.info(f"Début compression archive {compression_id}")
            start_time = timezone.now()
            
            # Dossier temporaire
            temp_job_dir = os.path.join(self.temp_dir, compression_id)
            os.makedirs(temp_job_dir, exist_ok=True)
            
            try:
                # Récupération des fichiers sources
                source_paths = self._prepare_source_files(compression_info, temp_job_dir)
                
                if not source_paths:
                    raise Exception("Aucun fichier source trouvé")
                
                # Compression selon le format
                archive_path = self._create_archive(compression_info, source_paths, temp_job_dir)
                
                # Upload vers storage
                storage_path = self._upload_archive(compression_info, archive_path)
                
                # Finalisation
                archive_size = os.path.getsize(archive_path)
                compression_time = (timezone.now() - start_time).total_seconds()
                
                compression_info.update({
                    'status': 'completed',
                    'completed_at': timezone.now().isoformat(),
                    'archive_size': archive_size,
                    'compression_ratio': archive_size / compression_info['total_source_size'],
                    'compression_time': compression_time,
                    'download_url': default_storage.url(storage_path)
                })
                
                logger.info(f"Compression archive {compression_id} terminée")
                return True
                
            finally:
                # Nettoyage
                if os.path.exists(temp_job_dir):
                    shutil.rmtree(temp_job_dir)
                    
        except Exception as e:
            logger.error(f"Erreur compression {compression_id}: {str(e)}")
            compression_info['status'] = 'failed'
            compression_info['error_message'] = str(e)[:500]
            return False
    
    def _prepare_source_files(self, compression_info: Dict[str, Any], temp_dir: str) -> List[str]:
        """Prépare les fichiers sources pour compression"""
        source_paths = []
        
        for file_info in compression_info['source_files_info']:
            filename = file_info['name']
            # Les fichiers sont supposés être dans uploads/compressions/
            storage_path = f"uploads/compressions/{filename}"
            
            if default_storage.exists(storage_path):
                # Téléchargement vers le dossier temporaire
                local_path = os.path.join(temp_dir, filename)
                with default_storage.open(storage_path, 'rb') as source_file:
                    with open(local_path, 'wb') as temp_file:
                        temp_file.write(source_file.read())
                source_paths.append(local_path)
            else:
                logger.warning(f"Fichier source non trouvé: {storage_path}")
        
        return source_paths
    
    def _create_archive(self, compression_info: Dict[str, Any], source_paths: List[str], 
                       temp_dir: str) -> str:
        """Crée l'archive selon le format"""
        format_name = compression_info['output_format'].lower()
        
        if format_name == 'zip':
            return self._create_zip_archive(compression_info, source_paths, temp_dir)
        else:
            raise ValueError(f"Format non implémenté: {format_name}")
    
    def _create_zip_archive(self, compression_info: Dict[str, Any], source_paths: List[str],
                           temp_dir: str) -> str:
        """Crée une archive ZIP"""
        archive_filename = f"archive_{compression_info['id'][:8]}.zip"
        archive_path = os.path.join(temp_dir, archive_filename)
        
        # Niveau de compression
        format_config = self.supported_formats['zip']
        compresslevel = format_config['compression_levels'].get(
            compression_info['compression_level'], 6
        )
        
        # Création de l'archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, 
                            compresslevel=compresslevel) as zf:
            
            # Mot de passe si demandé
            if compression_info['password_protected'] and compression_info.get('password'):
                zf.setpassword(compression_info['password'].encode())
            
            for source_path in source_paths:
                arcname = os.path.basename(source_path)
                zf.write(source_path, arcname)
        
        # Mise à jour du nom de fichier
        compression_info['archive_filename'] = archive_filename
        
        return archive_path
    
    def _upload_archive(self, compression_info: Dict[str, Any], archive_path: str) -> str:
        """Upload l'archive vers le storage"""
        filename = compression_info['archive_filename']
        storage_path = f"compressions/{compression_info['brand_id']}/{compression_info['id']}/{filename}"
        
        with open(archive_path, 'rb') as archive_file:
            saved_path = default_storage.save(storage_path, archive_file)
        
        return saved_path
    
    def get_compression_stats(self, brand_id: int) -> Dict[str, Any]:
        """Statistiques de compression pour une brand (version basique)"""
        # Pour l'instant, retourne des stats vides car pas de modèle DB
        return {
            'total_compressions': 0,
            'successful_compressions': 0,
            'success_rate': 0,
            'average_compression_ratio': 0,
            'space_saved_percentage': 0,
            'total_space_saved_bytes': 0,
            'total_space_saved_mb': 0
        }