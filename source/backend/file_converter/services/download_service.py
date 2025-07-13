# backend/file_converter/services/download_service.py

import os
import logging
import urllib.parse
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings

from ..utils import get_user_brands

logger = logging.getLogger(__name__)

class DownloadService:
    """Service dédié au téléchargement sécurisé de fichiers"""
    
    def __init__(self):
        self.mime_types = {
            'md': 'text/markdown',
            'txt': 'text/plain',
            'html': 'text/html',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        self.chunk_size = 8192
    
    def download_conversion(self, conversion, user) -> HttpResponse:
        """Télécharge un fichier de conversion avec sécurité renforcée"""
        
        # Validation des permissions
        self._validate_download_permissions(conversion, user)
        
        # Validation de l'état
        self._validate_conversion_state(conversion)
        
        # Obtenir le chemin du fichier
        file_path = self._get_secure_file_path(conversion)
        
        # Générer le nom de téléchargement
        download_filename = self._generate_download_filename(conversion)
        
        # Détermine si on fait du streaming (pour les gros fichiers)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # > 10MB
            return self._stream_file_download(file_path, download_filename, conversion.output_format.name)
        else:
            return self._direct_file_download(file_path, download_filename, conversion.output_format.name)
    
    def _validate_download_permissions(self, conversion, user):
        """Valide les permissions de téléchargement"""
        user_brands = get_user_brands(user)
        if conversion.brand not in user_brands:
            logger.warning(f"Tentative d'accès non autorisé - User {user.id} → Conversion {conversion.id}")
            raise PermissionDenied("Accès non autorisé à cette conversion")
    
    def _validate_conversion_state(self, conversion):
        """Valide l'état de la conversion"""
        if conversion.status != 'completed':
            raise ValueError('Conversion non terminée')
        
        if conversion.expires_at and conversion.expires_at < timezone.now():
            raise ValueError('Fichier expiré')
    
    def _get_secure_file_path(self, conversion):
        """Obtient le chemin du fichier de manière sécurisée"""
        from .conversion_service import ConversionService
        
        service = ConversionService()
        file_path = service._get_output_file_path(conversion, conversion.output_filename)
        
        # 🔧 Amélioration de la validation sécuritaire
        try:
            # Obtenir le chemin absolu du storage root
            if hasattr(settings, 'FILE_CONVERTER_STORAGE_ROOT'):
                allowed_base = os.path.abspath(settings.FILE_CONVERTER_STORAGE_ROOT)
            else:
                # Fallback vers le dossier storage dans BASE_DIR
                allowed_base = os.path.abspath(os.path.join(settings.BASE_DIR, 'storage', 'file_conversions'))
            
            # Normaliser les chemins
            file_path_abs = os.path.abspath(file_path)
            
            logger.debug(f"🔍 Validation chemin fichier:")
            logger.debug(f"   file_path: {file_path}")
            logger.debug(f"   file_path_abs: {file_path_abs}")
            logger.debug(f"   allowed_base: {allowed_base}")
            logger.debug(f"   file exists: {os.path.exists(file_path_abs)}")
            
            # Vérifier que le fichier est dans le dossier autorisé
            if not file_path_abs.startswith(allowed_base):
                logger.error(f"🚫 Tentative d'accès chemin non autorisé:")
                logger.error(f"   Fichier: {file_path_abs}")
                logger.error(f"   Base autorisée: {allowed_base}")
                raise PermissionDenied("Chemin de fichier non autorisé")
            
            # Vérifier que le fichier existe
            if not os.path.exists(file_path_abs):
                logger.error(f"🚫 Fichier non trouvé: {file_path_abs}")
                raise Http404('Fichier non trouvé')
            
            logger.info(f"✅ Chemin validé: {file_path_abs}")
            return file_path_abs
            
        except Exception as e:
            logger.error(f"❌ Erreur validation chemin: {str(e)}")
            if isinstance(e, (PermissionDenied, Http404)):
                raise
            else:
                raise Http404('Erreur accès fichier')
    
    def _generate_download_filename(self, conversion):
        """Génère un nom de fichier de téléchargement propre"""
        original_name = conversion.original_filename or "converted_file"
        output_format = conversion.output_format.name
        
        # Extraire le nom de base et nettoyer
        base_name = os.path.splitext(original_name)[0]
        
        # Nettoyer tout en préservant les caractères UTF-8 valides
        clean_chars = []
        for char in base_name:
            if char.isalnum() or char in (' ', '-', '_', '.'):
                clean_chars.append(char)
            elif ord(char) > 127:  # Caractères Unicode
                clean_chars.append(char)
        
        clean_base_name = ''.join(clean_chars).strip()
        
        if not clean_base_name:
            clean_base_name = "converted_file"
        
        return f"{clean_base_name}.{output_format}"
    
    def _get_mime_type(self, format_name):
        """Retourne le MIME type pour un format"""
        return self.mime_types.get(format_name.lower(), 'application/octet-stream')
    
    def _direct_file_download(self, file_path, filename, format_name):
        """Téléchargement direct pour petits fichiers"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            response = HttpResponse(
                file_content,
                content_type=self._get_mime_type(format_name)
            )
            
            self._set_download_headers(response, filename)
            
            logger.info(f"✅ Téléchargement direct: {filename} ({len(file_content)} bytes)")
            return response
            
        except Exception as e:
            logger.error(f"Erreur téléchargement direct {filename}: {str(e)}")
            raise
    
    def _stream_file_download(self, file_path, filename, format_name):
        """Téléchargement en streaming pour gros fichiers"""
        try:
            def file_iterator():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        yield chunk
            
            response = StreamingHttpResponse(
                file_iterator(),
                content_type=self._get_mime_type(format_name)
            )
            
            # Taille du fichier pour le header Content-Length
            file_size = os.path.getsize(file_path)
            response['Content-Length'] = str(file_size)
            
            self._set_download_headers(response, filename)
            
            logger.info(f"✅ Téléchargement streaming: {filename} ({file_size} bytes)")
            return response
            
        except Exception as e:
            logger.error(f"Erreur téléchargement streaming {filename}: {str(e)}")
            raise
    
    def _set_download_headers(self, response, filename):
        """Configure les headers de téléchargement"""
        # Encodage RFC 6266 pour support international
        encoded_filename = urllib.parse.quote(filename, safe='')
        
        # Double protection : filename normal + filename* encodé
        response['Content-Disposition'] = (
            f'attachment; '
            f'filename="{filename}"; '
            f'filename*=UTF-8\'\'{encoded_filename}'
        )
        
        # Headers de cache et sécurité
        response['Cache-Control'] = 'private, max-age=3600'
        response['X-Content-Type-Options'] = 'nosniff'