# backend/file_converter/services/converters/document_converter.py

import subprocess
import logging
import os
from typing import Dict
from .base_converter import BaseConverter, ConversionError, DependencyError

logger = logging.getLogger(__name__)

class DocumentConverter(BaseConverter):
    """Convertisseur LibreOffice pour documents office"""
    
    def __init__(self):
        super().__init__()
        self.supported_inputs = [
            'docx', 'doc', 'odt', 'rtf', 'txt', 'md', 'html',
            'xlsx', 'xls', 'ods', 'csv',
            'pptx', 'ppt', 'odp'
        ]
        self.supported_outputs = [
            'pdf', 'docx', 'odt', 'html', 'txt', 'md',
            'xlsx', 'csv', 'ods',
            'pptx', 'odp'
        ]
        self.required_dependencies = ['libreoffice']
    
    def get_converter_priority(self) -> int:
        return 30  # Priorité moyenne
    
    def convert(self, input_path: str, output_path: str, 
                input_format: str, output_format: str, 
                options: Dict = None) -> bool:
        """Conversion avec LibreOffice en mode headless"""
        
        self.validate_files(input_path, output_path)
        
        if not self.can_convert(input_format, output_format):
            raise ConversionError(f"Conversion {input_format} → {output_format} non supportée")
        
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            raise DependencyError(f"LibreOffice non disponible. Installer avec: apt-get install libreoffice")
        
        try:
            # Commande LibreOffice headless
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', output_format,
                '--outdir', os.path.dirname(output_path),
                input_path
            ]
            
            # Options spécifiques
            if options:
                if options.get('pdf_version'):
                    cmd.extend(['--pdf-version', options['pdf_version']])
                if options.get('quality'):
                    cmd.extend(['--quality', str(options['quality'])])
            
            logger.info(f"Exécution LibreOffice: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes max
                check=True
            )
            
            # LibreOffice génère automatiquement le nom, on doit le renommer
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            generated_file = os.path.join(
                os.path.dirname(output_path),
                f"{base_name}.{output_format}"
            )
            
            if os.path.exists(generated_file) and generated_file != output_path:
                os.rename(generated_file, output_path)
            
            if not os.path.exists(output_path):
                raise ConversionError("LibreOffice n'a pas généré le fichier de sortie")
            
            if os.path.getsize(output_path) == 0:
                raise ConversionError("LibreOffice a généré un fichier vide")
            
            logger.info(f"Conversion LibreOffice réussie: {input_path} → {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            raise ConversionError("Timeout de conversion LibreOffice (5 minutes)")
        except subprocess.CalledProcessError as e:
            error_msg = f"Erreur LibreOffice: {e.stderr or e.stdout or 'Erreur inconnue'}"
            logger.error(error_msg)
            raise ConversionError(error_msg)
        except Exception as e:
            logger.error(f"Erreur inattendue LibreOffice: {str(e)}")
            raise ConversionError(f"Erreur de conversion LibreOffice: {str(e)}")

class PandocConverter(BaseConverter):
    """Convertisseur Pandoc pour les formats markdown/text"""
    
    def __init__(self):
        super().__init__()
        self.supported_inputs = ['md', 'html', 'txt', 'docx', 'epub', 'latex']
        self.supported_outputs = ['md', 'html', 'pdf', 'docx', 'epub', 'latex', 'txt']
        self.required_dependencies = ['pandoc']
    
    def get_converter_priority(self) -> int:
        return 20  # Priorité élevée pour markdown/text
    
    def convert(self, input_path: str, output_path: str, 
                input_format: str, output_format: str, 
                options: Dict = None) -> bool:
        """Conversion avec Pandoc"""
        
        self.validate_files(input_path, output_path)
        
        if not self.can_convert(input_format, output_format):
            raise ConversionError(f"Conversion {input_format} → {output_format} non supportée par Pandoc")
        
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            raise DependencyError(f"Pandoc non disponible. Installer avec: apt-get install pandoc")
        
        try:
            cmd = [
                'pandoc',
                '-f', input_format,
                '-t', output_format,
                '-o', output_path,
                input_path
            ]
            
            # Options Pandoc
            if options:
                if options.get('toc'):
                    cmd.append('--toc')
                if options.get('standalone'):
                    cmd.append('--standalone')
                if options.get('template'):
                    cmd.extend(['--template', options['template']])
                if options.get('css'):
                    cmd.extend(['--css', options['css']])
            
            logger.info(f"Exécution Pandoc: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minutes
                check=True
            )
            
            if not os.path.exists(output_path):
                raise ConversionError("Pandoc n'a pas généré le fichier de sortie")
            
            if os.path.getsize(output_path) == 0:
                raise ConversionError("Pandoc a généré un fichier vide")
            
            logger.info(f"Conversion Pandoc réussie: {input_path} → {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            raise ConversionError("Timeout de conversion Pandoc (3 minutes)")
        except subprocess.CalledProcessError as e:
            error_msg = f"Erreur Pandoc: {e.stderr or e.stdout or 'Erreur inconnue'}"
            logger.error(error_msg)
            raise ConversionError(error_msg)
        except Exception as e:
            logger.error(f"Erreur inattendue Pandoc: {str(e)}")
            raise ConversionError(f"Erreur de conversion Pandoc: {str(e)}")