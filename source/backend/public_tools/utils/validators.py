# backend/public_tools/utils/validators.py
from django.core.exceptions import ValidationError
import magic
import mimetypes

def validate_file_content(file):
    """
    Validation du contenu réel du fichier (pas seulement l'extension)
    """
    try:
        # Lit les premiers bytes pour déterminer le type réel
        file.seek(0)
        file_content = file.read(1024)
        file.seek(0)
        
        # Utilise python-magic pour la détection
        mime_type = magic.from_buffer(file_content, mime=True)
        
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/zip',  # Pour les .docx, .xlsx
            'image/jpeg',
            'image/png',
            'text/plain',
        ]
        
        if mime_type not in allowed_types:
            raise ValidationError(f"Type de fichier détecté non autorisé: {mime_type}")
        
        return True
        
    except Exception as e:
        raise ValidationError(f"Erreur lors de la validation du fichier: {str(e)}")

def validate_no_malicious_content(content):
    """
    Validation basique contre du contenu malicieux
    """
    malicious_patterns = [
        '<script',
        'javascript:',
        'data:text/html',
        '<?php',
        '<%',
        'eval(',
    ]
    
    content_lower = str(content).lower()
    for pattern in malicious_patterns:
        if pattern in content_lower:
            raise ValidationError(f"Contenu potentiellement malicieux détecté")
    
    return True