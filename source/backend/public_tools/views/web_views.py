# backend/public_tools/views/web_views.py
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging

from public_tools.permissions import PublicToolsOnly, WordPressDomainOnly
from public_tools.throttling import PublicToolsAnonThrottle, PublicToolsProcessThrottle
from public_tools.serializers.web_serializers import UrlShorteningRequestSerializer
from public_tools.models import ToolUsage

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Récupère l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def render_shortener(request):
    """Renvoie le HTML du raccourcisseur d'URL"""
    try:
        # Tracking de l'usage
        ip_address = get_client_ip(request)
        ToolUsage.objects.create(tool_name='shortener', ip_address=ip_address)
        
        context = {
            'tool_name': 'shortener',
            'tool_category': 'web',
            'api_base_url': request.build_absolute_uri('/public-tools/'),
        }
        
        html_content = render(request, 'public_tools/web/shortener.html', context).content.decode()
        
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur render_shortener: {str(e)}")
        return Response({'error': 'Erreur lors du rendu'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_url_shortening(request):
    """Traite le raccourcissement d'URL via API Django"""
    try:
        ip_address = get_client_ip(request)
        
        # Import local pour éviter dépendances circulaires
        from url_shortener.models import PublicShortUrl
        from url_shortener.serializers import PublicShortUrlCreateSerializer
        
        # Validation
        serializer = UrlShorteningRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'URL invalide', 
                'details': serializer.errors
            }, status=400)
        
        # Créer l'URL courte via Django
        public_serializer = PublicShortUrlCreateSerializer(
            data={'original_url': serializer.validated_data['url']},
            context={'request': request}
        )
        
        if not public_serializer.is_valid():
            return Response({
                'error': 'Erreur création URL courte',
                'details': public_serializer.errors
            }, status=400)
        
        public_url = public_serializer.save()
        
        logger.info(f"URL raccourcie créée: {public_url.short_id} pour {ip_address}")
        
        return Response({
            'status': 'success',
            'short_url': f"https://hiurl.fr/{public_url.short_id}",
            'short_id': public_url.short_id,
            'original_url': public_url.original_url,
            'expires_at': public_url.expires_at,
            'expires_in_days': 30,
            'click_count': 0
        }, status=201)
        
    except Exception as e:
        logger.error(f"Erreur process_url_shortening: {str(e)}")
        return Response({'error': 'Erreur serveur'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_url_shortening_server(request):
    """Version server-side pour WordPress - renvoie HTML directement"""
    try:
        ip_address = get_client_ip(request)
        
        # Import local
        from url_shortener.models import PublicShortUrl
        from url_shortener.serializers import PublicShortUrlCreateSerializer
        
        # Récupérer l'URL depuis POST
        original_url = request.POST.get('url') or request.data.get('url')
        
        if not original_url:
            error_html = '''
            <div class="shortener-error">
                <h4>❌ URL manquante</h4>
                <p>Veuillez saisir une URL à raccourcir.</p>
            </div>
            '''
            return HttpResponse(error_html)
        
        # Validation et création
        public_serializer = PublicShortUrlCreateSerializer(
            data={'original_url': original_url},
            context={'request': request}
        )
        
        if not public_serializer.is_valid():
            errors = public_serializer.errors
            error_html = f'''
            <div class="shortener-error">
                <h4>❌ URL invalide</h4>
                <p>{str(errors.get('original_url', ['Erreur de validation'])[0])}</p>
            </div>
            '''
            return HttpResponse(error_html)
        
        public_url = public_serializer.save()
        
        # HTML de succès
        result_html = f'''
<div class="shortener-success">
    <h4>✅ URL raccourcie avec succès !</h4>
    <div class="url-result">
        <p><strong>URL originale :</strong><br>
        <span class="original-url">{public_url.original_url}</span></p>
        
        <p><strong>URL courte :</strong><br>
        <a href="https://hiurl.fr/{public_url.short_id}" target="_blank" class="short-url">
            https://hiurl.fr/{public_url.short_id}
        </a></p>
        
        <div class="url-actions">
            <button onclick="humariCopyShortUrl()" class="copy-button">📋 Copier</button>
            <a href="https://hiurl.fr/{public_url.short_id}" target="_blank" class="test-button">🔗 Tester</a>
        </div>
        
        <div class="url-info">
            <small>🕒 Expire le : {public_url.expires_at.strftime('%d/%m/%Y')}</small>
        </div>
    </div>
</div>
        
        <script>
        function copyShortUrl() {{
            const shortUrl = 'https://hiurl.fr/{public_url.short_id}';
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(shortUrl).then(() => {{
                    const button = document.querySelector('.copy-button');
                    const originalText = button.textContent;
                    button.textContent = '✅ Copié !';
                    button.style.background = '#16a34a';
                    setTimeout(() => {{
                        button.textContent = originalText;
                        button.style.background = '';
                    }}, 2000);
                }});
            }} else {{
                // Fallback pour anciens navigateurs
                const textArea = document.createElement('textarea');
                textArea.value = shortUrl;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('URL copiée !');
            }}
        }}
        </script>
        
        <style>
        .shortener-success {{
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }}
        .shortener-error {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }}
        .shortener-error h4 {{
            color: #dc2626;
            margin: 0 0 10px 0;
        }}
        .url-result {{
            margin-top: 15px;
        }}
        .original-url {{
            font-family: monospace;
            background: #f8fafc;
            padding: 8px;
            border-radius: 4px;
            word-break: break-all;
            display: block;
            margin-top: 5px;
        }}
        .short-url {{
            font-family: monospace;
            font-weight: bold;
            color: #0ea5e9;
            text-decoration: none;
            background: #f8fafc;
            padding: 8px;
            border-radius: 4px;
            display: block;
            margin-top: 5px;
        }}
        .short-url:hover {{
            background: #e2e8f0;
        }}
        .url-actions {{
            margin: 15px 0;
            display: flex;
            gap: 10px;
        }}
        .copy-button, .test-button {{
            background: #0ea5e9;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.9rem;
            transition: background 0.3s;
        }}
        .copy-button:hover, .test-button:hover {{
            background: #0284c7;
        }}
        .url-info {{
            margin-top: 15px;
            padding: 10px;
            background: #f8fafc;
            border-radius: 4px;
            border-left: 4px solid #0ea5e9;
        }}
        .url-info small {{
            color: #64748b;
        }}
        </style>
        '''
        
        return HttpResponse(result_html)
        
    except Exception as e:
        logger.error(f"Erreur process_url_shortening_server: {str(e)}")
        error_html = '''
        <div class="shortener-error">
            <h4>❌ Erreur serveur</h4>
            <p>Une erreur inattendue s'est produite. Veuillez réessayer.</p>
        </div>
        '''
        return HttpResponse(error_html)

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def render_qr_generator(request):
    """Renvoie le HTML du générateur QR (futur)"""
    return Response({'message': 'QR Generator - à implémenter'})

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_qr_generation(request):
    """Génère un QR code (futur)"""
    return Response({'message': 'QR Generation - à implémenter'})