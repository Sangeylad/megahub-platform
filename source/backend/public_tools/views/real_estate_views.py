# backend/public_tools/views/real_estate_views.py
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging

from public_tools.permissions import PublicToolsOnly, WordPressDomainOnly
from public_tools.throttling import PublicToolsAnonThrottle, PublicToolsProcessThrottle
from public_tools.serializers.real_estate_serializers import SimulationRequestSerializer

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def render_simulator(request):
    """
    Renvoie le HTML du simulateur immobilier
    """
    try:
        context = {
            'tool_name': 'simulator',
            'tool_category': 'real-estate',
            'api_base_url': request.build_absolute_uri('/public-tools/'),
        }
        
        html_content = render(request, 'public_tools/real_estate/simulator.html', context).content.decode()
        
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur render_simulator: {str(e)}")
        return Response({'error': 'Erreur lors du rendu'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_simulation(request):
    """
    Traite la simulation immobilière
    """
    process_simulation.tool_type = 'simulator'
    
    try:
        serializer = SimulationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Données invalides', 'details': serializer.errors}, status=400)
        
        # TODO: Implémenter la logique de simulation
        logger.info(f"Simulation demandée: {serializer.validated_data}")
        
        return Response({
            'status': 'success',
            'result': {
                'monthly_payment': 1200,  # TODO: calcul réel
                'total_interest': 50000,
                'total_cost': 250000
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur process_simulation: {str(e)}")
        return Response({'error': 'Erreur lors du traitement'}, status=500)

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def render_loan_calculator(request):
    """
    Renvoie le HTML de la calculette de prêt (futur)
    """
    return Response({'message': 'Loan Calculator - à implémenter'})

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_loan_calculation(request):
    """
    Calcule un prêt (futur)
    """
    return Response({'message': 'Loan Calculation - à implémenter'})

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_simulation_server(request):
    """
    Version server-side pour WordPress - renvoie HTML directement
    """
    process_simulation_server.tool_type = 'simulator'
    
    try:
        serializer = SimulationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            error_html = f'<div class="error">Données invalides: {serializer.errors}</div>'
            return HttpResponse(error_html)
        
        # TODO: Logique de simulation
        logger.info(f"Simulation server-side: {serializer.validated_data}")
        
        result_html = '''
        <div class="success">
            <p>✅ Simulation réalisée !</p>
            <div class="simulation-results">
                <p><strong>Mensualité:</strong> 1 200 €</p>
                <p><strong>Coût total:</strong> 250 000 €</p>
                <p><strong>Intérêts:</strong> 50 000 €</p>
            </div>
        </div>
        '''
        return HttpResponse(result_html)
        
    except Exception as e:
        logger.error(f"Erreur process_simulation_server: {str(e)}")
        error_html = '<div class="error">Erreur lors du traitement</div>'
        return HttpResponse(error_html)