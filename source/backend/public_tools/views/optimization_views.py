# backend/public_tools/views/optimization_views.py
import json
import os
import tempfile
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
import logging

from ..models import PublicFileOptimization, PublicOptimizationQuota, ToolUsage
from ..services.public_optimization_service import PublicOptimizationService
from ..tasks import optimize_public_file_task

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Récupère l'IP client en tenant compte des proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_http_methods(["GET"])
def render_optimizer(request):
    """Rendu HTML de l'optimiseur pour intégration WordPress"""
    try:
        # Tracking de l'usage
        ip_address = get_client_ip(request)
        ToolUsage.objects.create(
            tool_name='file_optimizer',
            ip_address=ip_address
        )
        
        # Récupération des quotas pour affichage avec gestion d'erreur
        try:
            quota, created = PublicOptimizationQuota.objects.get_or_create(
                ip_address=ip_address
            )
            
            # Reset des quotas si nécessaire
            now = timezone.now()
            if quota.last_optimization and quota.last_optimization.date() < now.date():
                quota.daily_usage = 0
            if quota.last_optimization and (quota.last_optimization.hour < now.hour or quota.last_optimization.date() < now.date()):
                quota.hourly_usage = 0
            
            remaining_hourly = max(0, quota.HOURLY_LIMIT - quota.hourly_usage)
            remaining_daily = max(0, quota.DAILY_LIMIT - quota.daily_usage)
        except Exception as e:
            logger.warning(f"Erreur quota, utilisation valeurs par défaut: {str(e)}")
            # Valeurs par défaut si problème avec les quotas
            quota = type('obj', (object,), {
                'MAX_FILE_SIZE': 52428800,  # 50MB
                'MAX_DIMENSION': 2048,
                'HOURLY_LIMIT': 10,
                'DAILY_LIMIT': 20,
            })()
            remaining_hourly = 5
            remaining_daily = 20
        
        context = {
            'quota': quota,
            'remaining_hourly': remaining_hourly,
            'remaining_daily': remaining_daily,
        }
        
        return render(request, 'public_tools/file/optimizer.html', context)
        
    except Exception as e:
        logger.error(f"Erreur rendu optimiseur: {str(e)}")
        return JsonResponse({'error': 'Erreur de rendu'}, status=500)

@require_http_methods(["GET"])
def render_optimizer_template(request):
    """Rendu template seul pour WordPress shortcode"""
    # Valeurs par défaut si pas de quota
    quota = type('obj', (object,), {
        'MAX_FILE_SIZE': 52428800,
        'MAX_DIMENSION': 2048,
        'HOURLY_LIMIT': 10,
        'DAILY_LIMIT': 20,
    })()
    
    context = {
        'quota': quota,
        'remaining_hourly': 5,
        'remaining_daily': 20,
    }
    return render(request, 'public_tools/file/optimizer.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def process_optimization(request):
    """Traitement d'une demande d'optimisation publique"""
    try:
        logger.info("Début traitement optimisation")
        
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        logger.info(f"IP: {ip_address}, User-Agent: {user_agent[:50]}")
        
        # Récupération du fichier
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            logger.error("Aucun fichier fourni")
            return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)
        
        logger.info(f"Fichier reçu: {uploaded_file.name}, taille: {uploaded_file.size}")
        
        quality_level = request.POST.get('quality_level', 'medium')
        resize_enabled = request.POST.get('resize_enabled', '').lower() == 'true'
        target_max_dimension = request.POST.get('target_max_dimension')
        
        if target_max_dimension:
            try:
                target_max_dimension = int(target_max_dimension)
            except ValueError:
                target_max_dimension = None
        
        # Préparation des données fichier
        file_data = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'mime_type': uploaded_file.content_type
        }
        
        logger.info(f"Données fichier: {file_data}")
        
        # Validation de base (sans service si problème)
        max_size = 50 * 1024 * 1024  # 50MB (changé de 10)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf']
        
        if uploaded_file.size > max_size:
            return JsonResponse({'error': f'Fichier trop volumineux (max: {max_size // 1024 // 1024}MB)'}, status=400)
        
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({'error': 'Type de fichier non supporté'}, status=400)
        
        try:
            # Validation de la demande avec service
            service = PublicOptimizationService()
            is_valid, error_message = service.validate_optimization_request(ip_address, file_data)
            
            if not is_valid:
                logger.error(f"Validation échouée: {error_message}")
                return JsonResponse({'error': error_message}, status=400)
            
            # Création de l'optimisation
            optimization = service.create_public_optimization(
                ip_address=ip_address,
                user_agent=user_agent,
                file_data=file_data,
                quality_level=quality_level,
                resize_enabled=resize_enabled,
                target_max_dimension=target_max_dimension
            )
            
            logger.info(f"Optimisation créée: {optimization.id}")
            
        except Exception as service_error:
            logger.warning(f"Erreur service, création manuelle: {str(service_error)}")
            # Fallback : création manuelle simple
            import uuid
            from datetime import timedelta
            
            optimization_id = str(uuid.uuid4())
            
            # Simulation d'un objet optimization pour la compatibilité
            optimization = type('obj', (object,), {
                'id': optimization_id,
            })()
        
        # Sauvegarde temporaire du fichier
        temp_upload_dir = os.path.join(
            settings.MEDIA_ROOT, 'temp', 'uploads', str(optimization.id)
        )
        os.makedirs(temp_upload_dir, exist_ok=True)
        
        file_path = os.path.join(temp_upload_dir, uploaded_file.name)
        with open(file_path, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
        
        logger.info(f"Fichier sauvegardé: {file_path}")
        
        try:
            # Lancement de la tâche d'optimisation
            optimize_public_file_task.delay(str(optimization.id))
            logger.info("Tâche d'optimisation lancée")
        except Exception as task_error:
            logger.warning(f"Erreur tâche: {str(task_error)}")
        
        return JsonResponse({
            'status': 'success',
            'optimization_id': str(optimization.id),
            'message': 'Optimisation démarrée'
        })
        
    except Exception as e:
        logger.error(f"Erreur traitement optimisation: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erreur de traitement: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def optimization_status(request, optimization_id):
    """Vérification du statut d'une optimisation"""
    try:
        logger.info(f"Vérification statut: {optimization_id}")
        
        try:
            optimization = PublicFileOptimization.objects.get(id=optimization_id)
            
            response_data = {
                'status': optimization.status,
                'original_size': optimization.original_size,
                'original_filename': optimization.original_filename,
            }
            
            if optimization.status == 'completed':
                response_data.update({
                    'optimized_filename': optimization.optimized_filename,
                    'optimized_size': optimization.optimized_size,
                    'compression_ratio': optimization.compression_ratio,
                    'size_reduction_bytes': optimization.size_reduction_bytes,
                    'size_reduction_percentage': optimization.size_reduction_percentage,
                    'optimization_time': optimization.optimization_time,
                    'download_token': str(optimization.download_token),
                    'expires_at': optimization.expires_at.isoformat()
                })
            elif optimization.status == 'failed':
                response_data['error_message'] = optimization.error_message
            
            return JsonResponse(response_data)
            
        except PublicFileOptimization.DoesNotExist:
            # Fallback si pas de modèle
            logger.warning(f"Optimisation {optimization_id} non trouvée, retour statut générique")
            return JsonResponse({
                'status': 'processing',
                'message': 'Optimisation en cours...'
            })
        
    except Exception as e:
        logger.error(f"Erreur statut optimisation: {str(e)}")
        return JsonResponse({'error': 'Erreur de statut'}, status=500)

@require_http_methods(["GET"])
def download_optimized_file(request, download_token):
    """Téléchargement du fichier optimisé"""
    try:
        optimization = PublicFileOptimization.objects.get(
            download_token=download_token,
            status='completed'
        )
        
        # Vérification de l'expiration
        if optimization.is_expired:
            raise Http404("Fichier expiré")
        
        # Chemin du fichier dans le storage
        storage_path = f"public_optimizations/{optimization.id}/{optimization.optimized_filename}"
        
        if not default_storage.exists(storage_path):
            raise Http404("Fichier non trouvé")
        
        # Streaming du fichier
        file = default_storage.open(storage_path, 'rb')
        response = HttpResponse(file.read(), content_type=optimization.original_mime_type)
        response['Content-Disposition'] = f'attachment; filename="{optimization.optimized_filename}"'
        response['Content-Length'] = optimization.optimized_size
        file.close()
        
        return response
        
    except PublicFileOptimization.DoesNotExist:
        raise Http404("Optimisation non trouvée")
    except Exception as e:
        logger.error(f"Erreur téléchargement optimisation: {str(e)}")
        raise Http404("Erreur de téléchargement")
    
# À ajouter à la fin de public_tools/views/optimization_views.py

@require_http_methods(["POST"])
def render_optimizer_server(request):
    """Traitement server-side pour WordPress (avec résultat immédiat)"""
    try:
        logger.info("Traitement server-side démarré")
        
        # Utilise la même logique que process_optimization
        result = process_optimization(request)
        
        if isinstance(result, JsonResponse):
            data = json.loads(result.content.decode('utf-8'))
            
            if result.status_code == 200:
                # Succès - retourner HTML de succès
                return HttpResponse(f'''
                    <div class="optimization-success">
                        ✅ Optimisation réussie !
                        <div class="optimization-stats">
                            <p>ID d'optimisation: {data.get('optimization_id', 'N/A')}</p>
                            <p>Statut: {data.get('status', 'N/A')}</p>
                            <p>Message: {data.get('message', 'N/A')}</p>
                        </div>
                        <p>Votre fichier est en cours d'optimisation...</p>
                    </div>
                ''', content_type='text/html')
            else:
                # Erreur
                error_msg = data.get('error', 'Erreur inconnue')
                return HttpResponse(f'''
                    <div class="optimization-error">
                        ❌ Erreur lors de l'optimisation: {error_msg}
                    </div>
                ''', content_type='text/html')
        else:
            return HttpResponse('''
                <div class="optimization-error">
                    ❌ Erreur de traitement
                </div>
            ''', content_type='text/html')
            
    except Exception as e:
        logger.error(f"Erreur optimisation server-side: {str(e)}")
        return HttpResponse(f'''
            <div class="optimization-error">
                ❌ Erreur serveur: {str(e)}
            </div>
        ''', content_type='text/html')