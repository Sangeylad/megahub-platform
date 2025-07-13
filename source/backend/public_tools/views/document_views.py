# backend/public_tools/views/document_views.py
import logging
import uuid
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils import timezone

from ..permissions import PublicToolsOnly, WordPressDomainOnly
from ..throttling import PublicToolsAnonThrottle, PublicToolsProcessThrottle
from ..serializers.document_serializers import (
    ConversionRequestSerializer, 
    BatchConversionRequestSerializer,
    PublicConversionStatusSerializer
)
from ..services.public_conversion_service import PublicConversionService
from ..models import PublicFileConversion, ToolUsage
from ..tasks import convert_public_file_task

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
def render_converter(request):
    """Renvoie le HTML du convertisseur pour WordPress"""
    try:
        # Tracking de l'usage
        ip_address = get_client_ip(request)
        ToolUsage.objects.create(tool_name='converter', ip_address=ip_address)
        
        # Formats disponibles pour l'interface
        available_formats = [
            {'value': 'pdf', 'label': 'PDF', 'icon': '📄', 'description': 'Format universel'},
            {'value': 'docx', 'label': 'Word (DOCX)', 'icon': '📝', 'description': 'Microsoft Word'},
            {'value': 'txt', 'label': 'Texte (TXT)', 'icon': '📋', 'description': 'Texte brut'},
            {'value': 'md', 'label': 'Markdown', 'icon': '🔖', 'description': 'Format Markdown'},
            {'value': 'html', 'label': 'HTML', 'icon': '🌐', 'description': 'Page web'}
        ]
        
        context = {
            'tool_name': 'converter',
            'tool_category': 'document',
            'api_base_url': request.build_absolute_uri('/public-tools/'),
            'conversion_id': None,
            'available_formats': available_formats,
            'supported_formats': {
                'input': ['pdf', 'docx', 'doc', 'txt', 'md', 'html'],
                'output': ['pdf', 'docx', 'txt', 'md', 'html']
            }
        }
        
        html_content = render(request, 'public_tools/document/converter.html', context).content.decode()
        
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur render_converter: {str(e)}")
        return Response({'error': 'Erreur lors du rendu'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_conversion(request):
    """Lance une conversion publique (un seul fichier)"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Validation des données
        serializer = ConversionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Données invalides', 
                'details': serializer.errors
            }, status=400)
        
        # Service de conversion publique
        service = PublicConversionService()
        
        try:
            # Créer la conversion
            conversion = service.create_public_conversion(
                ip_address=ip_address,
                user_agent=user_agent,
                file_obj=serializer.validated_data['file'],
                output_format=serializer.validated_data['target_format']
            )
            
            # Lancer la tâche asynchrone
            task = convert_public_file_task.delay(str(conversion.id))
            conversion.task_id = task.id
            conversion.save(update_fields=['task_id'])
            
            logger.info(f"Conversion publique lancée: {conversion.id} ({ip_address})")
            
            return Response({
                'status': 'success',
                'conversion_id': str(conversion.id),
                'filename': conversion.original_filename,
                'message': 'Conversion en cours...',
                'estimated_time': '30-60 secondes',
                'status_url': f"/public-tools/document/status/{conversion.id}/",
                'download_url': f"/public-tools/document/download/{conversion.download_token}/"
            }, status=201)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        
    except Exception as e:
        logger.error(f"Erreur process_conversion: {str(e)}")
        return Response({'error': 'Erreur serveur'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_batch_conversion(request):
    """Lance des conversions multiples (nouveau endpoint)"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Validation des données
        serializer = BatchConversionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Données invalides', 
                'details': serializer.errors
            }, status=400)
        
        service = PublicConversionService()
        conversions = []
        errors = []
        
        # Traiter chaque fichier
        for file_obj in serializer.validated_data['files']:
            try:
                conversion = service.create_public_conversion(
                    ip_address=ip_address,
                    user_agent=user_agent,
                    file_obj=file_obj,
                    output_format=serializer.validated_data['target_format']
                )
                
                # Lancer la tâche
                task = convert_public_file_task.delay(str(conversion.id))
                conversion.task_id = task.id
                conversion.save(update_fields=['task_id'])
                
                conversions.append({
                    'conversion_id': str(conversion.id),
                    'filename': conversion.original_filename,
                    'download_token': str(conversion.download_token)
                })
                
            except ValueError as e:
                errors.append({
                    'filename': file_obj.name,
                    'error': str(e)
                })
        
        logger.info(f"Batch conversion: {len(conversions)} succès, {len(errors)} erreurs ({ip_address})")
        
        return Response({
            'status': 'success' if conversions else 'error',
            'conversions': conversions,
            'errors': errors,
            'total_files': len(serializer.validated_data['files']),
            'successful_conversions': len(conversions),
            'failed_conversions': len(errors)
        }, status=201 if conversions else 400)
        
    except Exception as e:
        logger.error(f"Erreur process_batch_conversion: {str(e)}")
        return Response({'error': 'Erreur serveur'}, status=500)

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def conversion_status(request, conversion_id):
    """Vérifie le statut d'une conversion"""
    try:
        ip_address = get_client_ip(request)
        
        # Vérifier que la conversion appartient à cette IP
        conversion = PublicFileConversion.objects.get(
            id=conversion_id,
            ip_address=ip_address
        )
        
        serializer = PublicConversionStatusSerializer(conversion)
        return Response(serializer.data)
        
    except PublicFileConversion.DoesNotExist:
        return Response({'error': 'Conversion non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur status: {str(e)}")
        return Response({'error': 'Erreur serveur'}, status=500)

@api_view(['GET'])
@permission_classes([PublicToolsOnly])
@throttle_classes([PublicToolsAnonThrottle])
def download_converted_file(request, download_token):
    """Télécharge un fichier converti avec token"""
    try:
        service = PublicConversionService()
        file_path, filename = service.get_download_path(download_token)
        
        # Détecter le MIME type
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'html': 'text/html'
        }
        
        file_ext = filename.split('.')[-1].lower()
        content_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Lecture du fichier
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(file_content))
        response['Cache-Control'] = 'private, max-age=300'
        
        logger.info(f"Téléchargement public: {filename} ({len(file_content)} bytes)")
        return response
        
    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    except FileNotFoundError:
        return Response({'error': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        logger.error(f"Erreur download: {str(e)}")
        return Response({'error': 'Erreur téléchargement'}, status=500)

@api_view(['POST'])
@permission_classes([PublicToolsOnly, WordPressDomainOnly])
@throttle_classes([PublicToolsProcessThrottle])
@csrf_exempt
def process_conversion_server(request):
    """Version server-side pour WordPress - MISE À JOUR pour multiple files"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Récupérer les fichiers depuis la requête
        files = request.FILES.getlist('files[]') or [request.FILES.get('file')]
        files = [f for f in files if f is not None]
        
        if not files:
            error_html = '''
            <div class="conversion-error">
                <h4>❌ Aucun fichier reçu</h4>
                <p>Veuillez sélectionner au moins un fichier.</p>
            </div>
            '''
            return HttpResponse(error_html)
        
        target_format = request.POST.get('target_format')
        if not target_format:
            error_html = '''
            <div class="conversion-error">
                <h4>❌ Format de sortie manquant</h4>
                <p>Veuillez sélectionner un format de sortie.</p>
            </div>
            '''
            return HttpResponse(error_html)
        
        # Traitement séquentiel des fichiers
        service = PublicConversionService()
        conversions = []
        errors = []
        
        for file_obj in files:
            # Validation simple
            if file_obj.size > 10 * 1024 * 1024:
                errors.append(f"{file_obj.name}: Fichier trop volumineux (max 10MB)")
                continue
            
            try:
                conversion = service.create_public_conversion(
                    ip_address=ip_address,
                    user_agent=user_agent,
                    file_obj=file_obj,
                    output_format=target_format
                )
                
                # Lancer la tâche
                task = convert_public_file_task.delay(str(conversion.id))
                conversion.task_id = task.id
                conversion.save(update_fields=['task_id'])
                
                conversions.append(conversion)
                
            except ValueError as e:
                errors.append(f"{file_obj.name}: {str(e)}")
        
        if not conversions and errors:
            error_html = f'''
            <div class="conversion-error">
                <h4>❌ Erreurs de validation</h4>
                <ul>
                    {"".join([f"<li>{error}</li>" for error in errors])}
                </ul>
            </div>
            '''
            return HttpResponse(error_html)
        
        # HTML de résultat pour multiple files
        files_html = ""
        conversion_ids = []
        download_tokens = []
        
        for conv in conversions:
            files_html += f'''
            <div class="conversion-file-item">
                <span class="file-icon">📄</span>
                <span class="file-name">{conv.original_filename}</span>
                <span class="file-status" id="status-{conv.id}">🔄 En attente...</span>
            </div>
            '''
            conversion_ids.append(str(conv.id))
            download_tokens.append(str(conv.download_token))
        
        if errors:
            files_html += f'''
            <div class="conversion-errors">
                <h5>⚠️ Fichiers non traités:</h5>
                <ul>
                    {"".join([f"<li>{error}</li>" for error in errors])}
                </ul>
            </div>
            '''
        
        result_html = f'''
        <div class="conversion-success">
            <h4>✅ Conversion{'s' if len(conversions) > 1 else ''} lancée{'s' if len(conversions) > 1 else ''} !</h4>
            <p><strong>Fichier{'s' if len(conversions) > 1 else ''}:</strong> {len(conversions)} fichier{'s' if len(conversions) > 1 else ''}</p>
            <p><strong>Format de sortie:</strong> {target_format.upper()}</p>
            
            <div class="conversion-files">
                {files_html}
            </div>
            
            <div class="conversion-status" id="batch-status">
                <p>🔄 Conversions en cours...</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="batch-progress" style="width: 10%"></div>
                </div>
                <div class="progress-text" id="batch-progress-text">Initialisation...</div>
                <div id="download-container" style="display: none;">
                    <h5>📥 Téléchargements disponibles:</h5>
                    <div id="download-links"></div>
                </div>
            </div>
            
            <script>
            const ajaxUrl = '/wp-admin/admin-ajax.php';
            const conversionIds = {conversion_ids};
            const downloadTokens = {download_tokens};
            let completedCount = 0;
            let totalCount = conversionIds.length;
            let statusIntervals = [];
            
            function updateBatchProgress() {{
                const percentage = Math.round((completedCount / totalCount) * 100);
                const progressBar = document.getElementById('batch-progress');
                const progressText = document.getElementById('batch-progress-text');
                
                if (progressBar) progressBar.style.width = percentage + '%';
                if (progressText) {{
                    if (completedCount === totalCount) {{
                        progressText.textContent = '✅ Toutes les conversions terminées !';
                        document.getElementById('download-container').style.display = 'block';
                    }} else {{
                        progressText.textContent = `${{completedCount}}/${{totalCount}} conversions terminées`;
                    }}
                }}
            }}
            
            function checkConversionStatus(conversionId, index) {{
                return fetch(ajaxUrl + '?action=humari_conversion_status&conversion_id=' + conversionId)
                    .then(response => response.json())
                    .then(result => {{
                        if (!result.success) return;
                        
                        const data = result.data;
                        const statusElement = document.getElementById('status-' + conversionId);
                        
                        if (data.status === 'completed') {{
                            if (statusElement) statusElement.innerHTML = '✅ Terminé';
                            
                            // Ajouter le lien de téléchargement
                            const downloadContainer = document.getElementById('download-links');
                            if (downloadContainer) {{
                                const downloadLink = document.createElement('a');
                                downloadLink.href = ajaxUrl + '?action=humari_download_file&token=' + downloadTokens[index];
                                downloadLink.className = 'download-button';
                                downloadLink.download = true;
                                downloadLink.textContent = '📥 ' + data.original_filename.replace(/\.[^/.]+$/, "") + '.{target_format}';
                                downloadContainer.appendChild(downloadLink);
                            }}
                            
                            completedCount++;
                            updateBatchProgress();
                            
                            // Arrêter le polling pour cette conversion
                            if (statusIntervals[index]) {{
                                clearInterval(statusIntervals[index]);
                                statusIntervals[index] = null;
                            }}
                            
                        }} else if (data.status === 'failed') {{
                            if (statusElement) statusElement.innerHTML = '❌ Échec';
                            completedCount++;
                            updateBatchProgress();
                            
                            if (statusIntervals[index]) {{
                                clearInterval(statusIntervals[index]);
                                statusIntervals[index] = null;
                            }}
                            
                        }} else if (data.status === 'processing') {{
                            if (statusElement) statusElement.innerHTML = '🔄 Traitement...';
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error checking status for', conversionId, error);
                    }});
            }}
            
            // Démarrer le polling pour chaque conversion
            conversionIds.forEach((conversionId, index) => {{
                statusIntervals[index] = setInterval(() => {{
                    checkConversionStatus(conversionId, index);
                }}, 2000);
                
                // Check initial après 1 seconde
                setTimeout(() => checkConversionStatus(conversionId, index), 1000);
            }});
            
            // Arrêter tous les intervals après 5 minutes
            setTimeout(() => {{
                statusIntervals.forEach(interval => {{
                    if (interval) clearInterval(interval);
                }});
            }}, 300000);
            </script>
            
            <style>
            .conversion-success {{
                background: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
            }}
            .conversion-files {{
                margin: 15px 0;
                background: #f8fafc;
                border-radius: 6px;
                padding: 15px;
            }}
            .conversion-file-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 8px;
                padding: 8px;
                background: white;
                border-radius: 4px;
                border: 1px solid #e2e8f0;
            }}
            .file-icon {{ font-size: 1.2rem; }}
            .file-name {{ 
                flex: 1; 
                font-weight: 600; 
                color: #334155;
            }}
            .file-status {{ 
                font-size: 0.9rem;
                padding: 4px 8px;
                border-radius: 4px;
                background: #f1f5f9;
            }}
            .conversion-errors {{
                margin-top: 15px;
                padding: 10px;
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
            }}
            .conversion-errors h5 {{
                margin: 0 0 8px 0;
                color: #dc2626;
            }}
            .conversion-errors ul {{
                margin: 0;
                padding-left: 20px;
                color: #991b1b;
            }}
            .progress-bar {{
                width: 100%;
                height: 12px;
                background: #e5e7eb;
                border-radius: 6px;
                overflow: hidden;
                margin: 15px 0 10px 0;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #0ea5e9, #06b6d4);
                transition: width 0.5s ease;
                border-radius: 6px;
            }}
            .progress-text {{
                font-size: 0.9rem;
                color: #374151;
                text-align: center;
                margin-bottom: 15px;
            }}
            #download-container {{
                margin-top: 20px;
                padding: 15px;
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 6px;
            }}
            #download-container h5 {{
                margin: 0 0 10px 0;
                color: #166534;
            }}
            .download-button {{
                display: inline-block;
                background: #16a34a;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
                margin: 4px 8px 4px 0;
                font-size: 0.9rem;
                transition: background 0.3s;
            }}
            .download-button:hover {{
                background: #15803d;
                color: white;
            }}
            </style>
        </div>
        '''
        
        return HttpResponse(result_html)
        
    except Exception as e:
        logger.error(f"Erreur process_conversion_server: {str(e)}")
        error_html = '''
        <div class="conversion-error">
            <h4>❌ Erreur serveur</h4>
            <p>Une erreur inattendue s'est produite. Veuillez réessayer.</p>
        </div>
        '''
        return HttpResponse(error_html)

# Endpoints pour le debugging (à supprimer en prod)
@api_view(['GET'])
@permission_classes([PublicToolsOnly])
def debug_conversions(request):
    """Debug des conversions publiques (dev seulement)"""
    if not request.user.is_superuser:
        return Response({'error': 'Non autorisé'}, status=403)
    
    conversions = PublicFileConversion.objects.all()[:20]
    data = []
    
    for conv in conversions:
        data.append({
            'id': str(conv.id),
            'ip': conv.ip_address,
            'filename': conv.original_filename,
            'status': conv.status,
            'created': conv.created_at,
            'expires': conv.expires_at,
            'is_expired': conv.is_expired
        })
    
    return Response({'conversions': data})