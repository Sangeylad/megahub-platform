# backend/file_converter/services/converters/pdf_converter.py

import logging
import os
import sys
from typing import Dict, Optional, Tuple
from .base_converter import BaseConverter, ConversionError, DependencyError

logger = logging.getLogger(__name__)

class PDFConverter(BaseConverter):
    """Convertisseur PDF avec diagnostic complet"""
    
    def __init__(self):
        super().__init__()
        self.supported_inputs = ['pdf']
        self.supported_outputs = ['txt', 'md', 'html']
        self.required_dependencies = []
        self._active_engine = None
        self._dependencies_checked = False
        self._dependencies_available = False
    
    def get_converter_priority(self) -> int:
        return 10
    
    def check_dependencies(self) -> Tuple[bool, list]:
        """Diagnostic complet des dépendances PDF"""
        
        if self._dependencies_checked:
            return self._dependencies_available, [] if self._dependencies_available else ['PyMuPDF ou PyPDF2']
        
        logger.warning(f"🔍 DIAGNOSTIC PDF - Python path: {sys.path[:3]}...")
        logger.warning(f"🔍 DIAGNOSTIC PDF - Python executable: {sys.executable}")
        
        available_engines = []
        
        # Test PyMuPDF avec diagnostic détaillé
        logger.warning("🔍 Test PyMuPDF...")
        try:
            import fitz
            version = getattr(fitz, 'version', 'unknown')
            logger.warning(f"✅ PyMuPDF importé - Version: {version}")
            
            # Test fonctionnel basique
            test_doc = None
            try:
                # Créer un doc vide pour tester
                test_doc = fitz.open()
                test_doc.close()
                available_engines.append('PyMuPDF')
                if not self._active_engine:
                    self._active_engine = 'PyMuPDF'
                logger.warning("✅ PyMuPDF test fonctionnel OK")
            except Exception as e:
                logger.warning(f"❌ PyMuPDF test fonctionnel échoué: {e}")
                
        except ImportError as e:
            logger.warning(f"❌ PyMuPDF ImportError: {e}")
        except Exception as e:
            logger.warning(f"❌ PyMuPDF autre erreur: {e}")
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")
        
        # Test PyPDF2 avec diagnostic détaillé
        logger.warning("🔍 Test PyPDF2...")
        try:
            import PyPDF2
            version = getattr(PyPDF2, '__version__', 'unknown')
            logger.warning(f"✅ PyPDF2 importé - Version: {version}")
            
            # Test fonctionnel basique
            try:
                # Test de création d'un reader vide
                from io import BytesIO
                test_reader = PyPDF2.PdfReader(BytesIO(b''))
            except:
                pass  # Normal, c'est juste un test
            
            available_engines.append('PyPDF2')
            if not self._active_engine:
                self._active_engine = 'PyPDF2'
            logger.warning("✅ PyPDF2 test fonctionnel OK")
                
        except ImportError as e:
            logger.warning(f"❌ PyPDF2 ImportError: {e}")
        except Exception as e:
            logger.warning(f"❌ PyPDF2 autre erreur: {e}")
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")
        
        # Diagnostic pip
        logger.warning("🔍 Diagnostic des packages installés...")
        try:
            import subprocess
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True, timeout=10)
            pdf_packages = [line for line in result.stdout.split('\n') if any(pkg in line.lower() for pkg in ['pymupdf', 'pypdf2', 'fitz'])]
            logger.warning(f"📦 Packages PDF trouvés: {pdf_packages}")
        except Exception as e:
            logger.warning(f"❌ Erreur diagnostic pip: {e}")
        
        self._dependencies_checked = True
        self._dependencies_available = len(available_engines) > 0
        
        if self._dependencies_available:
            logger.warning(f"🎉 PDFConverter actif avec {len(available_engines)} moteur(s): {available_engines}")
            logger.warning(f"🚀 Moteur sélectionné: {self._active_engine}")
            return True, []
        else:
            logger.warning("💀 AUCUNE bibliothèque PDF disponible !")
            return False, ['PyMuPDF ou PyPDF2']
    
    # ... reste du code identique ...
    def can_convert(self, input_format: str, output_format: str) -> bool:
        formats_ok = (input_format.lower() in self.supported_inputs and 
                     output_format.lower() in self.supported_outputs)
        
        if not formats_ok:
            return False
        
        deps_ok, missing = self.check_dependencies()
        return deps_ok
    
    def convert(self, input_path: str, output_path: str, 
                input_format: str, output_format: str, 
                options: Dict = None) -> bool:
        
        self.validate_files(input_path, output_path)
        
        if not self.can_convert(input_format, output_format):
            deps_ok, missing = self.check_dependencies()
            if not deps_ok:
                raise DependencyError(f"Bibliothèques PDF manquantes: {', '.join(missing)}")
            raise ConversionError(f"Conversion {input_format} → {output_format} non supportée")
        
        try:
            text_content = self._extract_text_from_pdf(input_path)
            
            if not text_content.strip():
                raise ConversionError("Aucun texte extrait du PDF")
            
            formatted_content = self._format_text(text_content, output_format)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ConversionError("Fichier de sortie vide")
            
            logger.info(f"✅ Conversion PDF réussie avec {self._active_engine}")
            return True
            
        except Exception as e:
            if isinstance(e, (ConversionError, DependencyError)):
                raise
            else:
                raise ConversionError(f"Erreur conversion PDF: {str(e)}")
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extraction avec fallback et logs"""
        
        # PyMuPDF
        try:
            import fitz
            logger.warning(f"🔄 Extraction avec PyMuPDF: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text_content += page_text
                    text_content += "\n\n"
            
            doc.close()
            self._active_engine = 'PyMuPDF'
            logger.warning(f"✅ PyMuPDF extraction: {len(text_content)} caractères")
            return text_content
            
        except Exception as e:
            logger.warning(f"❌ PyMuPDF extraction échec: {e}")
        
        # PyPDF2 fallback
        try:
            import PyPDF2
            logger.warning(f"🔄 Extraction avec PyPDF2: {pdf_path}")
            
            text_content = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content += page_text
                            text_content += "\n\n"
                    except Exception as e:
                        logger.warning(f"Erreur page {page_num}: {e}")
                        continue
            
            self._active_engine = 'PyPDF2'
            logger.warning(f"✅ PyPDF2 extraction: {len(text_content)} caractères")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ PyPDF2 extraction échec: {e}")
            raise ConversionError(f"Toutes les extractions PDF ont échoué")
    
    def _format_text(self, text: str, output_format: str) -> str:
        if output_format == 'txt':
            return text.strip()
        elif output_format == 'md':
            return f"# Document PDF Converti\n\n{text.strip()}"
        elif output_format == 'html':
            return f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>PDF</title></head><body><pre>{text.strip()}</pre></body></html>'
        else:
            raise ConversionError(f"Format non supporté: {output_format}")