# backend/file_converter/services/converters/image_converter.py

import logging
import os
from typing import Dict
from .base_converter import BaseConverter, ConversionError, DependencyError

logger = logging.getLogger(__name__)

class ImageConverter(BaseConverter):
    """Convertisseur pour les images avec Pillow"""
    
    def __init__(self):
        super().__init__()
        self.supported_inputs = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'tif']
        self.supported_outputs = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'pdf', 'tiff', 'tif']
        self.required_dependencies = ['PIL']
    
    def get_converter_priority(self) -> int:
        return 25  # Priorité moyenne-élevée pour images
    
    def check_dependencies(self):
        """Vérifie Pillow"""
        try:
            from PIL import Image
            return True, []
        except ImportError:
            return False, ['Pillow']
    
    def convert(self, input_path: str, output_path: str,
                input_format: str, output_format: str,
                options: Dict = None) -> bool:
        """Conversion d'images avec Pillow"""
        
        self.validate_files(input_path, output_path)
        
        if not self.can_convert(input_format, output_format):
            raise ConversionError(f"Conversion {input_format} → {output_format} non supportée")
        
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            raise DependencyError(f"Pillow non disponible. Installer avec: pip install Pillow")
        
        try:
            from PIL import Image
            
            with Image.open(input_path) as img:
                # Options de conversion
                save_kwargs = {}
                
                if options:
                    if options.get('quality') and output_format.lower() in ['jpg', 'jpeg']:
                        save_kwargs['quality'] = int(options['quality'])
                    if options.get('optimize'):
                        save_kwargs['optimize'] = True
                    if options.get('dpi'):
                        save_kwargs['dpi'] = (int(options['dpi']), int(options['dpi']))
                
                # Conversion spéciale pour PDF
                if output_format.lower() == 'pdf':
                    # Convertir en RGB si nécessaire
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    save_kwargs['format'] = 'PDF'
                    save_kwargs['resolution'] = 100.0  # DPI par défaut
                
                # Conversion vers JPEG : convertir en RGB
                elif output_format.lower() in ['jpg', 'jpeg']:
                    if img.mode in ['RGBA', 'P']:
                        # Créer un fond blanc pour la transparence
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                
                # Conversion PNG avec transparence
                elif output_format.lower() == 'png' and img.mode not in ['RGBA', 'P']:
                    if 'transparency' in img.info:
                        img = img.convert('RGBA')
                
                # Redimensionnement si demandé
                if options and options.get('resize'):
                    width, height = options['resize']
                    img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                
                # Sauvegarde
                img.save(output_path, **save_kwargs)
            
            if not os.path.exists(output_path):
                raise ConversionError("Pillow n'a pas généré le fichier de sortie")
            
            if os.path.getsize(output_path) == 0:
                raise ConversionError("Pillow a généré un fichier vide")
            
            logger.info(f"Conversion image réussie: {input_path} → {output_path}")
            return True
            
        except Exception as e:
            if isinstance(e, (ConversionError, DependencyError)):
                raise
            logger.error(f"Erreur conversion image: {str(e)}")
            raise ConversionError(f"Erreur de conversion image: {str(e)}")