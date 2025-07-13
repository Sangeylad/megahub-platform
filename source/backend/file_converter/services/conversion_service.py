# backend/file_converter/services/conversion_service.py

import os
import logging
import glob
import tempfile
from typing import Dict, List, Optional, Tuple
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta

from ..models import FileConversion, SupportedFormat, ConversionQuota

logger = logging.getLogger(__name__)

class ConversionService:
    """Service principal de gestion des conversions avec sélection intelligente"""
    
    def __init__(self):
        self.converters = self._initialize_converters()
        self.storage_root = 'file_conversions'
        self.format_aliases = self._get_format_aliases()
    
    def _initialize_converters(self) -> Dict:
        """Initialise les convertisseurs avec gestion d'erreurs robuste"""
        converters = {}
        
        # Configuration des convertisseurs (nom, module, classe, description)
        converter_configs = [
            ('gotenberg', 'gotenberg_converter', 'GotenbergConverter', 'Service Gotenberg professionnel'),
            ('pdf', 'pdf_converter', 'PDFConverter', 'Conversion PDF vers texte'),
            ('document', 'document_converter', 'DocumentConverter', 'Documents Office avec LibreOffice'),
            ('pandoc', 'document_converter', 'PandocConverter', 'Formats textuels avec Pandoc'),
            ('image', 'image_converter', 'ImageConverter', 'Images avec Pillow'),
        ]
        
        for key, module_name, class_name, description in converter_configs:
            try:
                # Import dynamique
                module = __import__(
                    f'file_converter.services.converters.{module_name}', 
                    fromlist=[class_name]
                )
                converter_class = getattr(module, class_name)
                converter = converter_class()
                
                # Vérifier les dépendances
                deps_ok, missing = converter.check_dependencies()
                if deps_ok:
                    converters[key] = converter
                    logger.info(f"✅ {class_name} activé - {description}")
                else:
                    logger.warning(f"⚠️ {class_name} désactivé - {description}")
                    logger.warning(f"   Dépendances manquantes: {', '.join(missing)}")
                    
            except ImportError as e:
                logger.warning(f"❌ Import {class_name} échoué: {e}")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation {class_name}: {e}")
        
        if not converters:
            logger.error("❌ Aucun convertisseur disponible !")
        else:
            logger.info(f"🔧 ConversionService initialisé avec {len(converters)} convertisseurs")
        
        return converters
    
    def _get_format_aliases(self) -> Dict[str, str]:
        """Dictionnaire de normalisation des formats"""
        return {
            # Markdown
            'markdown': 'md',
            'mdown': 'md',
            'mkd': 'md',
            'mkdn': 'md',
            
            # Images
            'jpeg': 'jpg',
            'jpe': 'jpg',
            'jfif': 'jpg',
            'tiff': 'tif',
            
            # HTML
            'htm': 'html',
            'xhtml': 'html',
            
            # Documents Office
            'word': 'docx',
            'excel': 'xlsx',
            'powerpoint': 'pptx',
            
            # Texte
            'text': 'txt',
            'plain': 'txt',
            
            # OpenDocument
            'opendocument': 'odt',
            
            # Rich Text
            'richtext': 'rtf',
        }
    
    def _normalize_format(self, format_name: str) -> str:
        """Normalise les noms de formats avec gestion des alias"""
        if not format_name:
            return ''
        
        normalized = format_name.lower().strip()
        
        # Retirer les points si présents (.md -> md)
        if normalized.startswith('.'):
            normalized = normalized[1:]
        
        # Appliquer les alias
        return self.format_aliases.get(normalized, normalized)
    
    def get_supported_formats(self) -> Dict[str, List[Dict]]:
        """Retourne les formats supportés par catégorie avec alias"""
        formats = SupportedFormat.objects.all()
        result = {}
        
        for format_obj in formats:
            if format_obj.category not in result:
                result[format_obj.category] = []
            
            # Trouver les alias pour ce format
            aliases = [alias for alias, normalized in self.format_aliases.items() 
                      if normalized == format_obj.name]
            
            result[format_obj.category].append({
                'name': format_obj.name,
                'mime_type': format_obj.mime_type,
                'is_input': format_obj.is_input,
                'is_output': format_obj.is_output,
                'aliases': aliases
            })
        
        return result
    
    def get_converter_for_formats(self, input_format: str, output_format: str):
        """Sélectionne le meilleur convertisseur par priorité"""
        
        input_norm = self._normalize_format(input_format)
        output_norm = self._normalize_format(output_format)
        
        available_converters = []
        
        for name, converter in self.converters.items():
            if converter.can_convert(input_norm, output_norm):
                priority = converter.get_converter_priority()
                available_converters.append((priority, name, converter))
        
        if not available_converters:
            logger.warning(f"Aucun convertisseur trouvé pour {input_norm} → {output_norm}")
            return None
        
        # Trier par priorité (plus bas = plus prioritaire)
        available_converters.sort(key=lambda x: x[0])
        
        selected = available_converters[0]
        logger.info(f"Convertisseur sélectionné: {selected[1]} (priorité: {selected[0]})")
        
        return selected[2]
    
    def can_convert(self, input_format: str, output_format: str) -> Tuple[bool, str]:
        """Vérifie si une conversion est possible avec normalisation"""
        
        input_normalized = self._normalize_format(input_format)
        output_normalized = self._normalize_format(output_format)
        
        logger.debug(f"Vérification conversion: {input_format} -> {input_normalized}, {output_format} -> {output_normalized}")
        
        try:
            input_fmt = SupportedFormat.objects.get(name=input_normalized)
            output_fmt = SupportedFormat.objects.get(name=output_normalized)
        except SupportedFormat.DoesNotExist:
            return False, f"Format non supporté (normalisés: {input_normalized} -> {output_normalized})"
        
        if not input_fmt.is_input:
            return False, f"Format {input_normalized} non supporté en entrée"
        
        if not output_fmt.is_output:
            return False, f"Format {output_normalized} non supporté en sortie"
        
        # Vérifier qu'un convertisseur peut gérer cette conversion
        converter = self.get_converter_for_formats(input_normalized, output_normalized)
        if converter:
            return True, f"Conversion possible via {converter.__class__.__name__}"
        
        return False, "Aucun convertisseur disponible pour cette conversion"
    
    def check_quota(self, brand, file_size: int) -> Tuple[bool, str]:
        """Vérifie les quotas de conversion"""
        quota, created = ConversionQuota.objects.get_or_create(
            brand=brand,
            defaults={
                'monthly_limit': 100,
                'current_month_usage': 0,
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'reset_date': timezone.now().replace(day=1) + timedelta(days=32)
            }
        )
        
        # Reset automatique si nouveau mois
        if timezone.now() >= quota.reset_date:
            quota.current_month_usage = 0
            quota.reset_date = timezone.now().replace(day=1) + timedelta(days=32)
            quota.save()
        
        return quota.can_convert(file_size)
    
    def get_storage_base_path(self):
        """Retourne le chemin de base absolu du storage"""
        if hasattr(settings, 'FILE_CONVERTER_STORAGE_ROOT'):
            base_path = os.path.abspath(settings.FILE_CONVERTER_STORAGE_ROOT)
        else:
            # Fallback vers storage dans BASE_DIR
            base_path = os.path.abspath(os.path.join(settings.BASE_DIR, 'storage', 'file_conversions'))
        
        # S'assurer que le dossier existe
        os.makedirs(base_path, exist_ok=True)
        
        logger.debug(f"🔍 Storage base path: {base_path}")
        return base_path
    
    def create_conversion(self, user, brand, file_obj, output_format: str, 
                     options: Dict = None) -> FileConversion:
        """Crée une nouvelle conversion avec normalisation des formats"""
        
        # Détection du format d'entrée
        file_ext = os.path.splitext(file_obj.name)[1][1:].lower()
        if not file_ext:
            raise ValueError("Impossible de déterminer le format du fichier")
        
        # Normaliser les formats
        input_normalized = self._normalize_format(file_ext)
        output_normalized = self._normalize_format(output_format)
        
        logger.info(f"Création conversion: {file_ext} -> {input_normalized}, {output_format} -> {output_normalized}")
        
        try:
            input_format = SupportedFormat.objects.get(name=input_normalized)
            output_format_obj = SupportedFormat.objects.get(name=output_normalized)
        except SupportedFormat.DoesNotExist:
            raise ValueError(f"Format non supporté (normalisés: {input_normalized} -> {output_normalized})")
        
        # Vérification quota
        can_convert, error_msg = self.check_quota(brand, file_obj.size)
        if not can_convert:
            raise ValueError(error_msg)
        
        # Vérification conversion possible
        can_convert, error_msg = self.can_convert(file_ext, output_format)
        if not can_convert:
            raise ValueError(error_msg)
        
        # 🔧 CORRECTION : Nettoyage du nom de fichier AVANT sauvegarde
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        # Nettoyer le nom de fichier original
        original_name = file_obj.name
        clean_name = self._clean_filename(original_name)
        
        input_filename = f"{timestamp}_{clean_name}"
        
        # Utiliser le storage absolu
        base_path = self.get_storage_base_path()
        input_dir = os.path.join(base_path, 'inputs', str(brand.id))
        os.makedirs(input_dir, exist_ok=True)
        
        input_path = os.path.join(input_dir, input_filename)
        
        logger.info(f"🔧 Noms de fichiers:")
        logger.info(f"   Original: {original_name}")
        logger.info(f"   Nettoyé: {clean_name}")
        logger.info(f"   Final: {input_filename}")
        logger.info(f"   Chemin: {input_path}")
        
        # Sauvegarder le fichier directement
        with open(input_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        logger.info(f"✅ Fichier sauvegardé à: {input_path}")
        
        # Création de l'enregistrement
        conversion = FileConversion.objects.create(
            user=user,
            brand=brand,
            original_filename=original_name,  # Garder le nom original pour l'affichage
            original_size=file_obj.size,
            input_format=input_format,
            output_format=output_format_obj,
            status='pending'
        )
        
        return conversion

    def _clean_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier pour éviter les problèmes de système de fichiers"""
        if not filename:
            return "file"
        
        # Séparer nom et extension
        name, ext = os.path.splitext(filename)
        
        # Caractères autorisés : alphanumériques, espaces, tirets, underscores, points
        clean_chars = []
        for char in name:
            if char.isalnum() or char in (' ', '-', '_', '.'):
                clean_chars.append(char)
            elif ord(char) > 127:  # Caractères Unicode (accents)
                clean_chars.append(char)
            else:
                clean_chars.append('_')  # Remplacer les caractères problématiques
        
        clean_name = ''.join(clean_chars).strip()
        
        # Éviter les noms vides
        if not clean_name:
            clean_name = "file"
        
        # Limiter la longueur
        if len(clean_name) > 100:
            clean_name = clean_name[:100]
        
        return f"{clean_name}{ext}"
    
    def perform_conversion(self, conversion_id: int) -> bool:
        """Effectue la conversion avec gestion d'erreurs complète"""
        try:
            conversion = FileConversion.objects.get(id=conversion_id)
            conversion.status = 'processing'
            conversion.save()
            
            input_format = conversion.input_format.name
            output_format = conversion.output_format.name
            
            logger.info(f"Début conversion {conversion_id}: {conversion.original_filename} ({input_format} → {output_format})")
            
            # Sélection du convertisseur
            converter = self.get_converter_for_formats(input_format, output_format)
            
            if not converter:
                raise ValueError(f"Aucun convertisseur disponible pour {input_format} → {output_format}")
            
            # Chemins des fichiers
            input_path = self._get_input_file_path(conversion)
            output_filename = self._generate_output_filename(conversion)
            output_path = self._get_output_file_path(conversion, output_filename)
            
            # Vérifier que le fichier d'entrée existe
            if not os.path.exists(input_path):
                raise ValueError(f"Fichier d'entrée non trouvé: {input_path}")
            
            # Conversion
            start_time = timezone.now()
            conversion_options = self._get_conversion_options(conversion)
            
            success = converter.convert(
                input_path=input_path,
                output_path=output_path,
                input_format=input_format,
                output_format=output_format,
                options=conversion_options
            )
            
            if success and os.path.exists(output_path):
                self._finalize_successful_conversion(conversion, output_filename, output_path, start_time)
                return True
            else:
                self._mark_conversion_failed(conversion, "Échec de la conversion - fichier de sortie non généré")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion {conversion_id}: {str(e)}")
            try:
                conversion = FileConversion.objects.get(id=conversion_id)
                self._mark_conversion_failed(conversion, str(e))
            except:
                pass
            return False
    
    def _finalize_successful_conversion(self, conversion, output_filename, output_path, start_time):
        """Finalise une conversion réussie"""
        output_size = os.path.getsize(output_path)
        
        conversion.status = 'completed'
        conversion.completed_at = timezone.now()
        conversion.conversion_time = (timezone.now() - start_time).total_seconds()
        conversion.output_filename = output_filename
        conversion.output_size = output_size
        conversion.download_url = f"/api/file-converter/download/{conversion.id}/"
        conversion.expires_at = timezone.now() + timedelta(hours=24)
        conversion.save()
        
        # Incrémenter le quota
        try:
            quota = ConversionQuota.objects.get(brand=conversion.brand)
            quota.increment_usage()
        except ConversionQuota.DoesNotExist:
            pass
        
        logger.info(f"✅ Conversion {conversion.id} réussie en {conversion.conversion_time:.2f}s - Taille: {output_size} bytes")
    
    def _mark_conversion_failed(self, conversion, error_message):
        """Marque une conversion comme échouée"""
        conversion.status = 'failed'
        conversion.error_message = error_message[:500]
        conversion.save()
        
        logger.error(f"❌ Conversion {conversion.id} échouée: {error_message}")
    
    def _get_conversion_options(self, conversion: FileConversion) -> Dict:
        """Retourne les options de conversion selon le type"""
        options = {}
        
        input_format = conversion.input_format.name
        output_format = conversion.output_format.name
        
        # Options spécifiques PDF
        if input_format == 'pdf':
            if conversion.original_size > 10 * 1024 * 1024:  # > 10MB
                options.update({
                    'extract_media': False,
                    'encoding': 'UTF-8'
                })
        
        # Options Markdown
        if output_format == 'md':
            options.update({
                'wrap': 'none',
                'extract_media': False
            })
        
        # Options HTML
        if output_format == 'html':
            options.update({
                'standalone': True
            })
        
        return options
    
    def _get_input_file_path(self, conversion: FileConversion) -> str:
        """Génère le chemin du fichier d'entrée avec recherche robuste"""
        base_path = self.get_storage_base_path()
        timestamp = conversion.created_at.strftime('%Y%m%d_%H%M%S')
        
        # 🔧 CORRECTION : Utiliser le nom nettoyé pour la recherche
        clean_original = self._clean_filename(conversion.original_filename)
        filename = f"{timestamp}_{clean_original}"
        
        # Chemin attendu
        expected_path = os.path.join(base_path, 'inputs', str(conversion.brand.id), filename)
        
        logger.debug(f"🔍 Recherche fichier d'entrée:")
        logger.debug(f"   Original filename: {conversion.original_filename}")
        logger.debug(f"   Clean filename: {clean_original}")
        logger.debug(f"   Timestamp: {timestamp}")
        logger.debug(f"   Nom attendu: {filename}")
        logger.debug(f"   Chemin attendu: {expected_path}")
        logger.debug(f"   Fichier existe: {os.path.exists(expected_path)}")
        
        # Vérifier si le fichier existe au chemin prévu
        if os.path.exists(expected_path):
            logger.info(f"✅ Fichier trouvé: {expected_path}")
            return expected_path
        
        # 🔧 Recherche de fallback améliorée
        input_dir = os.path.join(base_path, 'inputs', str(conversion.brand.id))
        if os.path.exists(input_dir):
            # 1. Chercher par pattern de timestamp exact
            pattern1 = os.path.join(input_dir, f"{timestamp}_*")
            matches1 = glob.glob(pattern1)
            
            logger.debug(f"🔍 Pattern 1 ({timestamp}_*): {matches1}")
            
            if matches1:
                # Prendre le premier match
                found_file = matches1[0]
                logger.info(f"✅ Fichier trouvé via pattern timestamp: {found_file}")
                return found_file
            
            # 2. Chercher par heure (au cas où les secondes diffèrent)
            hour_timestamp = conversion.created_at.strftime('%Y%m%d_%H%M')
            pattern2 = os.path.join(input_dir, f"{hour_timestamp}*")
            matches2 = glob.glob(pattern2)
            
            logger.debug(f"🔍 Pattern 2 ({hour_timestamp}*): {matches2}")
            
            if matches2:
                # Prendre le plus récent dans cette heure
                latest_file = max(matches2, key=os.path.getctime)
                logger.info(f"✅ Fichier trouvé via pattern heure: {latest_file}")
                return latest_file
            
            # 3. Chercher le fichier le plus récent de la brand
            try:
                all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                            if os.path.isfile(os.path.join(input_dir, f))]
                if all_files:
                    latest_file = max(all_files, key=os.path.getctime)
                    logger.warning(f"⚠️ Fallback vers fichier le plus récent: {latest_file}")
                    return latest_file
            except Exception as e:
                logger.error(f"Erreur recherche fallback: {e}")
            
            # Lister les fichiers disponibles pour debug
            available_files = os.listdir(input_dir)
            logger.error(f"❌ Fichier non trouvé. Fichiers disponibles: {available_files}")
        else:
            logger.error(f"❌ Dossier {input_dir} n'existe pas")
        
        raise ValueError(f"Fichier source introuvable: {expected_path}")
    
    
    def _generate_output_filename(self, conversion: FileConversion) -> str:
        """Génère le nom du fichier de sortie"""
        base_name = os.path.splitext(conversion.original_filename)[0]
        clean_base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        output_format = conversion.output_format.name
        
        if not clean_base_name:
            clean_base_name = "converted_file"
        
        return f"{clean_base_name}.{output_format}"
    
    def _get_output_file_path(self, conversion: FileConversion, filename: str) -> str:
        """Génère le chemin du fichier de sortie"""
        base_path = self.get_storage_base_path()
        output_dir = os.path.join(base_path, 'outputs', str(conversion.brand.id))
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        
        logger.debug(f"🔍 Génération chemin sortie:")
        logger.debug(f"   base_path: {base_path}")
        logger.debug(f"   output_dir: {output_dir}")
        logger.debug(f"   filename: {filename}")
        logger.debug(f"   file_path: {file_path}")
        
        return file_path
    
    def cleanup_expired_files(self) -> Dict[str, int]:
        """Nettoie les fichiers expirés"""
        cleaned = {'conversions': 0, 'files': 0}
        
        try:
            expired_conversions = FileConversion.objects.filter(
                expires_at__lt=timezone.now(),
                status='completed'
            )
            
            for conversion in expired_conversions:
                try:
                    # Supprimer le fichier de sortie
                    if conversion.output_filename:
                        output_path = self._get_output_file_path(conversion, conversion.output_filename)
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            cleaned['files'] += 1
                    
                    # Supprimer le fichier d'entrée
                    try:
                        input_path = self._get_input_file_path(conversion)
                        if os.path.exists(input_path):
                            os.remove(input_path)
                            cleaned['files'] += 1
                    except ValueError:
                        pass
                    
                    conversion.delete()
                    cleaned['conversions'] += 1
                    
                except Exception as e:
                    logger.error(f"Erreur nettoyage conversion {conversion.id}: {str(e)}")
            
            logger.info(f"Nettoyage terminé: {cleaned['conversions']} conversions, {cleaned['files']} fichiers")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage général: {str(e)}")
        
        return cleaned
    
    def get_conversion_statistics(self, brand) -> Dict:
        """Retourne les statistiques de conversion pour une brand"""
        from django.db.models import Count, Avg, Sum
        
        conversions = FileConversion.objects.filter(brand=brand)
        
        stats = {
            'total_conversions': conversions.count(),
            'completed': conversions.filter(status='completed').count(),
            'failed': conversions.filter(status='failed').count(),
            'pending': conversions.filter(status__in=['pending', 'processing']).count(),
            'total_size_processed': conversions.filter(status='completed').aggregate(
                total=Sum('original_size')
            )['total'] or 0,
            'avg_conversion_time': conversions.filter(
                status='completed',
                conversion_time__isnull=False
            ).aggregate(avg=Avg('conversion_time'))['avg'],
            'popular_input_formats': list(conversions.values(
                'input_format__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]),
            'popular_output_formats': list(conversions.values(
                'output_format__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5])
        }
        
        return stats