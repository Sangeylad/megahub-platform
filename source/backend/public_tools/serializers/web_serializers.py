# backend/public_tools/serializers/web_serializers.py
from rest_framework import serializers
import re
from urllib.parse import urlparse

class UrlShorteningRequestSerializer(serializers.Serializer):
    """Serializer pour raccourcissement d'URL via WordPress"""
    
    url = serializers.URLField(max_length=2000)
    
    def validate_url(self, value):
        """Validation sécurisée de l'URL"""
        
        # 1. Validation format de base
        try:
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                raise serializers.ValidationError("Format d'URL invalide")
        except Exception:
            raise serializers.ValidationError("Format d'URL invalide")
        
        # 2. Protocoles autorisés
        if parsed.scheme not in ['http', 'https']:
            raise serializers.ValidationError("Seuls les protocoles HTTP et HTTPS sont autorisés")
        
        # 3. Domaines bloqués
        hostname = parsed.netloc.lower()
        blocked_domains = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '10.', '192.168.', '172.16.', '172.17.',
            '169.254.', 'bit.ly', 'tinyurl.com', 't.co'
        ]
        
        for blocked in blocked_domains:
            if blocked in hostname:
                raise serializers.ValidationError(f"Domaine non autorisé: {hostname}")
        
        # 4. Patterns suspects
        suspicious_patterns = [
            r'\.\./', r'<script', r'javascript:', r'data:',
            r'eval\(', r'exec\(', r'system\(', r'shell\('
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError("URL contient des éléments suspects")
        
        # 5. Longueur maximale pour public
        if len(value) > 1000:
            raise serializers.ValidationError("URL trop longue pour usage public (max 1000 caractères)")
        
        return value

class QrGenerationRequestSerializer(serializers.Serializer):
    """Serializer pour génération QR code (futur)"""
    
    data = serializers.CharField(max_length=500)
    size = serializers.IntegerField(min_value=100, max_value=1000, default=300)
    format = serializers.ChoiceField(choices=['PNG', 'JPEG', 'SVG'], default='PNG')
    
    def validate_data(self, value):
        """Validation du contenu QR"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Contenu requis")
        
        # Patterns suspects
        suspicious_patterns = ['<script', 'javascript:', 'eval(']
        for pattern in suspicious_patterns:
            if pattern in value.lower():
                raise serializers.ValidationError("Contenu suspect détecté")
        
        return value