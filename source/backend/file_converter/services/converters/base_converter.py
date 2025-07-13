# backend/file_converter/services/converters/base_converter.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class ConversionError(Exception):
    """Exception spécifique aux conversions"""
    pass

class DependencyError(ConversionError):
    """Exception pour les dépendances manquantes"""
    pass

class BaseConverter(ABC):
    """Classe abstraite pour tous les convertisseurs"""
    
    def __init__(self):
        self.supported_inputs: List[str] = []
        self.supported_outputs: List[str] = []
        self.temp_dir = tempfile.gettempdir()
        self.required_dependencies: List[str] = []
        self._dependency_check_cache = {}
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str,
                input_format: str, output_format: str,
                options: Dict = None) -> bool:
        """
        Convertit un fichier d'un format à un autre
        
        Args:
            input_path: Chemin du fichier source
            output_path: Chemin du fichier de destination
            input_format: Format source (ex: 'docx')
            output_format: Format cible (ex: 'pdf')
            options: Options de conversion spécifiques
        
        Returns:
            bool: True si succès, False sinon
        
        Raises:
            ConversionError: En cas d'erreur de conversion
        """
        pass
    
    def can_convert(self, input_format: str, output_format: str) -> bool:
        """Vérifie si la conversion est supportée ET les dépendances disponibles"""
        formats_ok = (input_format.lower() in self.supported_inputs and 
                     output_format.lower() in self.supported_outputs)
        
        if not formats_ok:
            return False
        
        # Vérifier les dépendances uniquement si nécessaire
        if self.required_dependencies:
            deps_ok, _ = self.check_dependencies()
            return deps_ok
        
        return True
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """Vérifie les dépendances requises"""
        if not self.required_dependencies:
            return True, []
        
        missing = []
        for dependency in self.required_dependencies:
            if dependency not in self._dependency_check_cache:
                try:
                    if dependency == 'libreoffice':
                        import subprocess
                        result = subprocess.run(['libreoffice', '--version'], 
                                              capture_output=True, timeout=5)
                        self._dependency_check_cache[dependency] = result.returncode == 0
                    elif dependency == 'pandoc':
                        import subprocess
                        result = subprocess.run(['pandoc', '--version'], 
                                              capture_output=True, timeout=5)
                        self._dependency_check_cache[dependency] = result.returncode == 0
                    else:
                        __import__(dependency)
                        self._dependency_check_cache[dependency] = True
                except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
                    self._dependency_check_cache[dependency] = False
            
            if not self._dependency_check_cache[dependency]:
                missing.append(dependency)
        
        return len(missing) == 0, missing
    
    def get_converter_priority(self) -> int:
        """Priorité du convertisseur (plus bas = plus prioritaire)"""
        return 50
    
    def validate_files(self, input_path: str, output_path: str) -> bool:
        """Valide les chemins d'entrée et sortie"""
        if not os.path.exists(input_path):
            raise ConversionError(f"Fichier source introuvable: {input_path}")
        
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        return True
    
    def get_file_info(self, file_path: str) -> Dict:
        """Retourne les infos d'un fichier"""
        if not os.path.exists(file_path):
            raise ConversionError(f"Fichier inexistant: {file_path}")
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'name': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1].lower()
        }