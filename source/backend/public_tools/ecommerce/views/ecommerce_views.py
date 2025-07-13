# backend/public_tools/ecommerce/views/ecommerce_views.py
import logging
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import render

from ...permissions import PublicToolsOnly
from ...throttling import PublicToolsAnonThrottle
from ...models import ToolUsage

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
def render_roas_calculator(request):
    """Renvoie le HTML du simulateur e-commerce"""
    try:
        # Tracking de l'usage
        ip_address = get_client_ip(request)
        ToolUsage.objects.create(tool_name='ecommerce_simulator', ip_address=ip_address)
        
        context = {
            'tool_name': 'ecommerce_simulator',
            'tool_category': 'ecommerce'
        }
        
        html_content = render(request, 'public_tools/ecommerce/roas_calculator.html', context).content.decode()
        
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur render_roas_calculator: {str(e)}")
        return Response({'error': 'Erreur lors du rendu'}, status=500)
