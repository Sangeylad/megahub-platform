# backend/file_converter/services/converters/gotenberg_converter.py

import logging
import os
import requests
import tempfile
from typing import Dict
from .base_converter import BaseConverter, ConversionError, DependencyError

logger = logging.getLogger(__name__)

class GotenbergConverter(BaseConverter):
    """Convertisseur utilisant le service Gotenberg pour PDF et documents"""
    
    def __init__(self):
        super().__init__()
        self.supported_inputs = [
            'pdf',  # PDF vers texte
            'docx', 'doc', 'odt', 'rtf',  # Documents Office
            'html', 'url'  # Web vers PDF
        ]
        self.supported_outputs = [
            'pdf',  # Documents vers PDF
            'txt', 'md', 'html'  # PDF vers texte
        ]
        self.gotenberg_url = 'http://gotenberg:3000'
        self.required_dependencies = ['requests']
    
    def get_converter_priority(self) -> int:
        return 5  # Priorité très élevée (mieux que PyMuPDF)
    
    def check_dependencies(self) -> tuple[bool, list]:
        """Vérifie que Gotenberg est accessible"""
        try:
            response = requests.get(f"{self.gotenberg_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Gotenberg service accessible")
                return True, []
            else:
                logger.warning(f"❌ Gotenberg health check failed: {response.status_code}")
                return False, ['Gotenberg service']
        except Exception as e:
            logger.warning(f"❌ Gotenberg inaccessible: {e}")
            return False, ['Gotenberg service']
    
    def convert(self, input_path: str, output_path: str, 
                input_format: str, output_format: str, 
                options: Dict = None) -> bool:
        """Conversion via Gotenberg API"""
        
        self.validate_files(input_path, output_path)
        
        if not self.can_convert(input_format, output_format):
            raise ConversionError(f"Conversion {input_format} → {output_format} non supportée par Gotenberg")
        
        try:
            if input_format == 'pdf' and output_format in ['txt', 'md', 'html']:
                return self._pdf_to_text(input_path, output_path, output_format, options)
            elif input_format in ['docx', 'doc', 'odt', 'rtf', 'html'] and output_format == 'pdf':
                return self._document_to_pdf(input_path, output_path, input_format, options)
            else:
                raise ConversionError(f"Combinaison {input_format} → {output_format} non implémentée")
                
        except Exception as e:
            if isinstance(e, (ConversionError, DependencyError)):
                raise
            else:
                raise ConversionError(f"Erreur Gotenberg: {str(e)}")
    
    def _pdf_to_text(self, input_path: str, output_path: str, output_format: str, options: Dict = None) -> bool:
        """Convertit PDF vers texte via extraction simple"""
        
        # Pour PDF → texte, on utilise les bibliothèques Python en fallback
        # Car Gotenberg est plutôt pour générer des PDF, pas les lire
        try:
            # Essayer PyMuPDF d'abord
            try:
                import fitz
                return self._extract_pdf_with_pymupdf(input_path, output_path, output_format)
            except ImportError:
                pass
            
            # Fallback PyPDF2
            try:
                import PyPDF2
                return self._extract_pdf_with_pypdf2(input_path, output_path, output_format)
            except ImportError:
                pass
            
            # Si aucune bibliothèque PDF Python disponible, on convertit via LibreOffice
            return self._pdf_via_libreoffice(input_path, output_path, output_format)
            
        except Exception as e:
            raise ConversionError(f"Extraction PDF échouée: {str(e)}")
    
    def _extract_pdf_with_pymupdf(self, input_path: str, output_path: str, output_format: str) -> bool:
        """Extraction PyMuPDF"""
        import fitz
        
        doc = fitz.open(input_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
            text_content += "\n\n"
        
        doc.close()
        
        if not text_content.strip():
            raise ConversionError("Aucun texte extrait du PDF")
        
        formatted_content = self._format_text_content(text_content, output_format)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        logger.info(f"✅ PDF extraction PyMuPDF réussie: {len(text_content)} caractères")
        return True
    
    def _extract_pdf_with_pypdf2(self, input_path: str, output_path: str, output_format: str) -> bool:
        """Extraction PyPDF2"""
        import PyPDF2
        
        text_content = ""
        
        with open(input_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                text_content += page.extract_text()
                text_content += "\n\n"
        
        if not text_content.strip():
            raise ConversionError("Aucun texte extrait du PDF")
        
        formatted_content = self._format_text_content(text_content, output_format)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        logger.info(f"✅ PDF extraction PyPDF2 réussie: {len(text_content)} caractères")
        return True
    
    def _pdf_via_libreoffice(self, input_path: str, output_path: str, output_format: str) -> bool:
        """Conversion via LibreOffice (dernier recours)"""
        import subprocess
        
        # Convertir PDF vers un format intermédiaire avec LibreOffice
        with tempfile.TemporaryDirectory() as temp_dir:
            # LibreOffice peut convertir PDF vers ODT/DOCX
            temp_docx = os.path.join(temp_dir, "temp.docx")
            
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'docx',
                '--outdir', temp_dir,
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Puis reconvertir le DOCX vers le format final
            if os.path.exists(temp_docx):
                return self._document_to_text_via_libreoffice(temp_docx, output_path, output_format)
            else:
                raise ConversionError("LibreOffice n'a pas pu convertir le PDF")
    
    def _document_to_pdf(self, input_path: str, output_path: str, input_format: str, options: Dict = None) -> bool:
        """Convertit document vers PDF via Gotenberg"""
        
        url = f"{self.gotenberg_url}/forms/libreoffice/convert"
        
        files = {
            'files': (os.path.basename(input_path), open(input_path, 'rb'))
        }
        
        data = {}
        if options:
            if options.get('landscape'):
                data['landscape'] = 'true'
            if options.get('quality'):
                data['quality'] = str(options['quality'])
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Document vers PDF via Gotenberg: {input_path}")
            return True
            
        except requests.RequestException as e:
            raise ConversionError(f"Erreur requête Gotenberg: {str(e)}")
        finally:
            files['files'][1].close()
    
    def _format_text_content(self, text: str, output_format: str) -> str:
        """Formate le texte selon le format de sortie"""
        
        text = text.strip()
        
        if output_format == 'txt':
            return text
        elif output_format == 'md':
            # Conversion basique vers Markdown
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    formatted_lines.append('')
                    continue
                
                # Détecter les titres
                if len(line) < 80 and (line.isupper() or line.count(' ') <= 3):
                    formatted_lines.append(f"## {line}")
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)
            
        elif output_format == 'html':
            # Conversion basique vers HTML
            return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Document Converti</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h2 {{ color: #333; margin-top: 30px; }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: inherit;">{text}</pre>
</body>
</html>'''
        else:
            raise ConversionError(f"Format de sortie non supporté: {output_format}")