# backend/public_tools/services/public_conversion_service.py
import os
import logging
import tempfile
from typing import Dict, Optional, Tuple
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile

from file_converter.services.conversion_service import ConversionService
from file_converter.models import SupportedFormat
from ..models import PublicFileConversion, PublicConversionQuota

logger = logging.getLogger(__name__)

class PublicConversionService:
    """Service de conversion pour les outils publics avec sécurité renforcée"""
    
    def __init__(self):
        # Réutiliser ton service existant
        self.conversion_service = ConversionService()
        self.storage_root = os.path.join(settings.BASE_DIR, 'storage', 'public_conversions')
        os.makedirs(self.storage_root, exist_ok=True)
        
        # Formats autorisés en public (restreints)
        self.allowed_inputs = ['pdf', 'docx', 'doc', 'txt', 'md', 'html']
        self.allowed_outputs = ['pdf', 'docx', 'txt', 'md', 'html']
    
    def check_quota(self, ip_address: str, file_size: int) -> Tuple[bool, str]:
        """Vérifie les quotas par IP"""
        quota, created = PublicConversionQuota.objects.get_or_create(
            ip_address=ip_address,
            defaults={'hourly_usage': 0, 'daily_usage': 0}
        )
        
        return quota.can_convert(file_size)
    
    def can_convert_public(self, input_format: str, output_format: str) -> Tuple[bool, str]:
        """Vérifie si la conversion est autorisée en public"""
        input_norm = self.conversion_service._normalize_format(input_format)
        output_norm = self.conversion_service._normalize_format(output_format)
        
        if input_norm not in self.allowed_inputs:
            return False, f"Format d'entrée non autorisé en public: {input_format}"
        
        if output_norm not in self.allowed_outputs:
            return False, f"Format de sortie non autorisé en public: {output_format}"
        
        # Utiliser la logique existante pour vérifier la conversion avec mapping
        mapped_input = self._map_format_for_converter(input_norm)
        mapped_output = self._map_format_for_converter(output_norm)
        
        return self.conversion_service.can_convert(mapped_input, mapped_output)
    
    def _map_format_for_converter(self, format_name: str, converter_name: str = None) -> str:
        """Mappe les formats selon le convertisseur utilisé"""
        
        # Mapping spécifique pour Pandoc
        pandoc_mapping = {
            'txt': 'plain',
            'md': 'markdown',
            'html': 'html',
            'docx': 'docx',
            'pdf': 'pdf'
        }
        
        # Mapping spécifique pour LibreOffice  
        libreoffice_mapping = {
            'txt': 'txt',
            'md': 'txt',    # LibreOffice ne fait pas de markdown natif
            'html': 'html',
            'docx': 'docx',
            'pdf': 'pdf'
        }
        
        # Mapping spécifique pour Gotenberg/PDF
        pdf_mapping = {
            'txt': 'txt',
            'md': 'md',
            'html': 'html',
            'docx': 'docx',
            'pdf': 'pdf'
        }
        
        # Si on sait quel convertisseur on utilise
        if converter_name:
            converter_lower = converter_name.lower()
            if 'pandoc' in converter_lower:
                return pandoc_mapping.get(format_name, format_name)
            elif 'libreoffice' in converter_lower or 'document' in converter_lower:
                return libreoffice_mapping.get(format_name, format_name)
            elif 'gotenberg' in converter_lower or 'pdf' in converter_lower:
                return pdf_mapping.get(format_name, format_name)
        
        # Mapping par défaut (pour Pandoc qui est souvent prioritaire)
        return pandoc_mapping.get(format_name, format_name)
    
    def create_public_conversion(self, ip_address: str, user_agent: str, 
                               file_obj, output_format: str) -> PublicFileConversion:
        """Crée une conversion publique"""
        
        # Détection du format d'entrée
        file_ext = os.path.splitext(file_obj.name)[1][1:].lower()
        if not file_ext:
            raise ValueError("Impossible de déterminer le format du fichier")
        
        # Vérifications
        can_convert, error_msg = self.can_convert_public(file_ext, output_format)
        if not can_convert:
            raise ValueError(error_msg)
        
        can_quota, error_msg = self.check_quota(ip_address, file_obj.size)
        if not can_quota:
            raise ValueError(error_msg)
        
        # Sauvegarde sécurisée du fichier
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        clean_name = self._clean_filename(file_obj.name)
        input_filename = f"{timestamp}_{clean_name}"
        
        input_dir = os.path.join(self.storage_root, 'inputs', ip_address.replace('.', '_'))
        os.makedirs(input_dir, exist_ok=True)
        input_path = os.path.join(input_dir, input_filename)
        
        # Sauvegarder le fichier
        with open(input_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        # Créer l'enregistrement
        conversion = PublicFileConversion.objects.create(
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else '',
            original_filename=file_obj.name,
            original_size=file_obj.size,
            input_format=file_ext,
            output_format=output_format,
            status='pending'
        )
        
        logger.info(f"Conversion publique créée: {conversion.id} ({ip_address})")
        return conversion
    
    def perform_public_conversion(self, conversion_id: str) -> bool:
        """Effectue la conversion publique en utilisant ton service existant"""
        try:
            conversion = PublicFileConversion.objects.get(id=conversion_id)
            conversion.status = 'processing'
            conversion.save()
            
            # Préparer les chemins
            input_path = self._get_input_path(conversion)
            output_filename = self._generate_output_filename(conversion)
            output_path = self._get_output_path(conversion, output_filename)
            
            # 🔧 CORRECTION : Mapper les formats pour le convertisseur
            input_format_raw = conversion.input_format
            output_format_raw = conversion.output_format
            
            # Obtenir le convertisseur d'abord pour savoir quel mapping utiliser
            input_format_mapped = self._map_format_for_converter(input_format_raw)
            output_format_mapped = self._map_format_for_converter(output_format_raw)
            
            converter = self.conversion_service.get_converter_for_formats(
                input_format_mapped,
                output_format_mapped
            )
            
            if not converter:
                # Essayer avec d'autres mappings
                converter_types = ['pandoc', 'libreoffice', 'gotenberg']
                for conv_type in converter_types:
                    input_mapped = self._map_format_for_converter(input_format_raw, conv_type)
                    output_mapped = self._map_format_for_converter(output_format_raw, conv_type)
                    
                    converter = self.conversion_service.get_converter_for_formats(
                        input_mapped, output_mapped
                    )
                    if converter:
                        input_format_mapped = input_mapped
                        output_format_mapped = output_mapped
                        logger.info(f"Convertisseur trouvé avec mapping {conv_type}: {converter.__class__.__name__}")
                        break
            
            if not converter:
                raise ValueError(f"Aucun convertisseur disponible pour {input_format_raw} → {output_format_raw}")
            
            # Log du convertisseur sélectionné
            converter_name = converter.__class__.__name__
            logger.info(f"Conversion {conversion_id} avec {converter_name}: {input_format_raw}({input_format_mapped}) → {output_format_raw}({output_format_mapped})")
            
            # Affiner le mapping selon le convertisseur réel
            if hasattr(converter, '__class__'):
                converter_class_name = converter.__class__.__name__
                input_format_mapped = self._map_format_for_converter(input_format_raw, converter_class_name)
                output_format_mapped = self._map_format_for_converter(output_format_raw, converter_class_name)
            
            # Conversion avec formats mappés
            start_time = timezone.now()
            success = converter.convert(
                input_path=input_path,
                output_path=output_path,
                input_format=input_format_mapped,
                output_format=output_format_mapped,
                options=self._get_conversion_options(conversion, converter_name)
            )
            
            if success and os.path.exists(output_path):
                self._finalize_conversion(conversion, output_filename, output_path, start_time)
                
                # Incrémenter quota
                try:
                    quota = PublicConversionQuota.objects.get(ip_address=conversion.ip_address)
                    quota.increment_usage()
                except PublicConversionQuota.DoesNotExist:
                    pass
                
                return True
            else:
                self._mark_failed(conversion, "Conversion échouée - fichier de sortie non généré")
                return False
                
        except Exception as e:
            logger.error(f"Erreur conversion publique {conversion_id}: {str(e)}")
            try:
                conversion = PublicFileConversion.objects.get(id=conversion_id)
                self._mark_failed(conversion, str(e))
            except:
                pass
            return False
    
    def _get_conversion_options(self, conversion: PublicFileConversion, converter_name: str) -> Dict:
        """Options de conversion selon le convertisseur"""
        options = {}
        
        input_format = conversion.input_format
        output_format = conversion.output_format
        
        # Options spécifiques selon le convertisseur
        if 'pandoc' in converter_name.lower():
            if output_format == 'html':
                options.update({
                    'standalone': True
                })
            elif output_format == 'pdf':
                options.update({
                    'pdf-engine': 'weasyprint'  # Si disponible
                })
        
        elif 'libreoffice' in converter_name.lower():
            if output_format == 'pdf':
                options.update({
                    'quality': 90
                })
        
        elif 'gotenberg' in converter_name.lower():
            if output_format == 'pdf':
                options.update({
                    'landscape': False,
                    'quality': 95
                })
        
        return options
    
    def get_download_path(self, download_token: str) -> Tuple[str, str]:
        """Retourne le chemin et nom du fichier pour téléchargement"""
        try:
            conversion = PublicFileConversion.objects.get(
                download_token=download_token,
                status='completed'
            )
            
            if conversion.is_expired:
                raise ValueError("Fichier expiré")
            
            output_path = self._get_output_path(conversion, conversion.output_filename)
            
            if not os.path.exists(output_path):
                raise ValueError("Fichier non trouvé")
            
            return output_path, conversion.output_filename
            
        except PublicFileConversion.DoesNotExist:
            raise ValueError("Token de téléchargement invalide")
    
    def cleanup_expired_files(self) -> Dict[str, int]:
        """Nettoyage agressif des fichiers expirés"""
        cleaned = {'conversions': 0, 'files': 0}
        
        try:
            expired_conversions = PublicFileConversion.objects.filter(
                expires_at__lt=timezone.now()
            )
            
            for conversion in expired_conversions:
                try:
                    # Supprimer fichiers
                    input_path = self._get_input_path(conversion)
                    if os.path.exists(input_path):
                        os.remove(input_path)
                        cleaned['files'] += 1
                    
                    if conversion.output_filename:
                        output_path = self._get_output_path(conversion, conversion.output_filename)
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            cleaned['files'] += 1
                    
                    conversion.delete()
                    cleaned['conversions'] += 1
                    
                except Exception as e:
                    logger.error(f"Erreur nettoyage {conversion.id}: {str(e)}")
            
            logger.info(f"Nettoyage public: {cleaned['conversions']} conversions, {cleaned['files']} fichiers")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage général: {str(e)}")
        
        return cleaned
    
    def _clean_filename(self, filename: str) -> str:
        """Nettoie le nom de fichier"""
        return self.conversion_service._clean_filename(filename)
    
    def _get_input_path(self, conversion: PublicFileConversion) -> str:
        """Chemin du fichier d'entrée"""
        timestamp = conversion.created_at.strftime('%Y%m%d_%H%M%S')
        clean_name = self._clean_filename(conversion.original_filename)
        filename = f"{timestamp}_{clean_name}"
        
        ip_folder = conversion.ip_address.replace('.', '_')
        expected_path = os.path.join(self.storage_root, 'inputs', ip_folder, filename)
        
        # Vérification d'existence avec fallback
        if os.path.exists(expected_path):
            return expected_path
        
        # Recherche avec pattern plus large
        input_dir = os.path.join(self.storage_root, 'inputs', ip_folder)
        if os.path.exists(input_dir):
            import glob
            
            # Pattern par timestamp
            pattern = os.path.join(input_dir, f"{timestamp}_*")
            matches = glob.glob(pattern)
            
            if matches:
                logger.warning(f"Fichier trouvé via pattern: {matches[0]} (attendu: {expected_path})")
                return matches[0]
        
        raise ValueError(f"Fichier source introuvable: {expected_path}")
    
    def _get_output_path(self, conversion: PublicFileConversion, filename: str) -> str:
        """Chemin du fichier de sortie"""
        ip_folder = conversion.ip_address.replace('.', '_')
        output_dir = os.path.join(self.storage_root, 'outputs', ip_folder)
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)
    
    def _generate_output_filename(self, conversion: PublicFileConversion) -> str:
        """Génère le nom du fichier de sortie"""
        base_name = os.path.splitext(conversion.original_filename)[0]
        clean_base = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if not clean_base:
            clean_base = "converted_file"
        
        return f"{clean_base}.{conversion.output_format}"
    
    def _finalize_conversion(self, conversion, output_filename, output_path, start_time):
        """Finalise une conversion réussie"""
        conversion.status = 'completed'
        conversion.completed_at = timezone.now()
        conversion.conversion_time = (timezone.now() - start_time).total_seconds()
        conversion.output_filename = output_filename
        conversion.output_size = os.path.getsize(output_path)
        conversion.save()
        
        logger.info(f"Conversion publique réussie: {conversion.id} en {conversion.conversion_time:.2f}s")
    
    def _mark_failed(self, conversion, error_message):
        """Marque comme échouée"""
        conversion.status = 'failed'
        conversion.error_message = error_message[:500]
        conversion.save()
        
        logger.error(f"Conversion publique échouée {conversion.id}: {error_message}")