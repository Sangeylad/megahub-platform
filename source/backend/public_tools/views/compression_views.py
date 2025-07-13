# backend/public_tools/views/compression_views.py
import json
import os
import tempfile
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

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
def render_compressor(request):
    """Rendu HTML du compresseur pour intégration WordPress"""
    try:
        # Tracking de l'usage
        ip_address = get_client_ip(request)
        ToolUsage.objects.create(
            tool_name='file_optimizer',
            ip_address=ip_address
        )
        
        # Récupération des quotas pour affichage
        quota, created = PublicOptimizationQuota.objects.get_or_create(
            ip_address=ip_address
        )
        
        # Reset des quotas si nécessaire
        now = timezone.now()
        if quota.last_optimization.date() < now.date():
            quota.daily_usage = 0
        if quota.last_optimization.hour < now.hour or quota.last_optimization.date() < now.date():
            quota.hourly_usage = 0
        
        remaining_hourly = max(0, quota.HOURLY_LIMIT - quota.hourly_usage)
        remaining_daily = max(0, quota.DAILY_LIMIT - quota.daily_usage)
        
        html_content = f'''
        <div id="megahub-file-optimizer" class="megahub-tool">
            <div class="optimizer-header">
                <h3>🗜️ Optimiseur de Fichiers</h3>
                <p>Réduisez le poids de vos PDF, images et documents</p>
            </div>
            
            <div class="optimizer-limits">
                <div class="limits-grid">
                    <div class="limit-item">
                        <span class="limit-label">Utilisations restantes (heure)</span>
                        <span class="limit-value">{remaining_hourly}/{quota.HOURLY_LIMIT}</span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Utilisations restantes (jour)</span>
                        <span class="limit-value">{remaining_daily}/{quota.DAILY_LIMIT}</span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Taille max fichier</span>
                        <span class="limit-value">{quota.MAX_FILE_SIZE // 1024 // 1024}MB</span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Résolution max</span>
                        <span class="limit-value">{quota.MAX_DIMENSION}px</span>
                    </div>
                </div>
            </div>
            
            <div class="optimizer-form">
                <div class="file-drop-zone" id="fileDropZone">
                    <div class="drop-zone-content">
                        <i class="fas fa-file-image drop-icon"></i>
                        <p class="drop-text">Glissez votre fichier ici ou <span class="browse-link">parcourez</span></p>
                        <p class="drop-hint">Formats: PDF, JPG, PNG, WebP (max {quota.MAX_FILE_SIZE // 1024 // 1024}MB)</p>
                    </div>
                    <input type="file" id="fileInput" accept=".pdf,.jpg,.jpeg,.png,.webp" style="display: none;">
                </div>
                
                <div class="file-info" id="fileInfo" style="display: none;">
                    <h4>Fichier sélectionné:</h4>
                    <div class="selected-file" id="selectedFile"></div>
                </div>
                
                <div class="optimizer-options" id="optimizerOptions" style="display: none;">
                    <h4>Options d'optimisation:</h4>
                    
                    <div class="option-group">
                        <label for="qualityLevel">Niveau de compression:</label>
                        <select id="qualityLevel" class="form-control">
                            <option value="low">Maximum (qualité réduite, poids minimal)</option>
                            <option value="medium" selected>Équilibré (bon compromis qualité/poids)</option>
                            <option value="high">Conservateur (qualité préservée)</option>
                        </select>
                    </div>
                    
                    <div class="option-group">
                        <label>
                            <input type="checkbox" id="resizeEnabled"> Redimensionner l'image
                        </label>
                        <div id="resizeOptions" style="display: none; margin-top: 10px;">
                            <label for="maxDimension">Dimension maximale (px):</label>
                            <input type="number" id="maxDimension" class="form-control" 
                                   min="100" max="{quota.MAX_DIMENSION}" value="1024" 
                                   placeholder="Largeur ou hauteur max">
                            <small class="form-text text-muted">La proportion sera conservée</small>
                        </div>
                    </div>
                </div>
                
                <div class="optimizer-actions">
                    <button id="optimizeBtn" class="btn btn-primary" disabled>
                        <i class="fas fa-magic"></i> Optimiser le fichier
                    </button>
                    <button id="clearBtn" class="btn btn-secondary" style="display: none;">
                        <i class="fas fa-times"></i> Effacer
                    </button>
                </div>
                
                <div class="optimization-progress" id="optimizationProgress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p class="progress-text" id="progressText">Analyse du fichier...</p>
                </div>
                
                <div class="optimization-result" id="optimizationResult" style="display: none;">
                    <div class="result-success">
                        <h4>✅ Optimisation terminée!</h4>
                        <div class="result-stats" id="resultStats"></div>
                        <div class="result-actions">
                            <a id="downloadLink" class="btn btn-success" download>
                                <i class="fas fa-download"></i> Télécharger le fichier optimisé
                            </a>
                            <button id="newOptimizationBtn" class="btn btn-outline-primary">
                                <i class="fas fa-plus"></i> Optimiser un autre fichier
                            </button>
                        </div>
                        <p class="result-warning">⚠️ Le fichier sera supprimé automatiquement dans 1 heure</p>
                    </div>
                </div>
                
                <div class="optimization-error" id="optimizationError" style="display: none;">
                    <div class="error-content">
                        <h4>❌ Erreur d'optimisation</h4>
                        <p class="error-message" id="errorMessage"></p>
                        <button id="retryBtn" class="btn btn-outline-primary">
                            <i class="fas fa-redo"></i> Réessayer
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="optimizer-tips">
                <h5>💡 Conseils d'optimisation</h5>
                <ul>
                    <li><strong>PDF</strong> : Réduit la taille des images intégrées et optimise la structure</li>
                    <li><strong>JPG</strong> : Ajuste la qualité de compression et redimensionne si nécessaire</li>
                    <li><strong>PNG</strong> : Réduit le nombre de couleurs et optimise la palette</li>
                    <li><strong>WebP</strong> : Format moderne avec compression avancée</li>
                </ul>
            </div>
        </div>

        <style>
        .megahub-tool {{
            max-width: 700px;
            margin: 20px auto;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .optimizer-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        
        .optimizer-header h3 {{
            margin: 0 0 8px 0;
            font-size: 24px;
            font-weight: 600;
        }}
        
        .optimizer-header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .optimizer-limits {{
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .limits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
        }}
        
        .limit-item {{
            text-align: center;
            padding: 8px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}
        
        .limit-label {{
            display: block;
            font-size: 12px;
            color: #64748b;
            margin-bottom: 4px;
        }}
        
        .limit-value {{
            display: block;
            font-weight: 600;
            color: #334155;
        }}
        
        .optimizer-form {{
            padding: 24px;
        }}
        
        .file-drop-zone {{
            border: 2px dashed #cbd5e0;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            background: #f7fafc;
        }}
        
        .file-drop-zone:hover {{
            border-color: #667eea;
            background: #f0f4ff;
        }}
        
        .file-drop-zone.drag-over {{
            border-color: #667eea;
            background: #e6f3ff;
            transform: scale(1.02);
        }}
        
        .drop-icon {{
            font-size: 48px;
            color: #94a3b8;
            margin-bottom: 16px;
        }}
        
        .drop-text {{
            font-size: 18px;
            color: #475569;
            margin-bottom: 8px;
        }}
        
        .browse-link {{
            color: #667eea;
            text-decoration: underline;
            cursor: pointer;
        }}
        
        .drop-hint {{
            font-size: 14px;
            color: #94a3b8;
            margin: 0;
        }}
        
        .file-info {{
            margin: 20px 0;
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        
        .file-info h4 {{
            margin: 0 0 16px 0;
            color: #334155;
            font-size: 16px;
        }}
        
        .selected-file {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        }}
        
        .file-details {{
            flex: 1;
        }}
        
        .file-name {{
            font-weight: 500;
            color: #334155;
            margin-bottom: 4px;
        }}
        
        .file-meta {{
            font-size: 12px;
            color: #94a3b8;
        }}
        
        .file-remove {{
            background: none;
            border: none;
            color: #ef4444;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
        }}
        
        .file-remove:hover {{
            background: #fee2e2;
        }}
        
        .optimizer-options {{
            margin: 20px 0;
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        
        .optimizer-options h4 {{
            margin: 0 0 16px 0;
            color: #334155;
            font-size: 16px;
        }}
        
        .option-group {{
            margin-bottom: 16px;
        }}
        
        .option-group label {{
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            color: #374151;
        }}
        
        .form-control {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }}
        
        .optimizer-actions {{
            display: flex;
            gap: 12px;
            margin: 24px 0;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover:not(:disabled) {{
            background: #5a67d8;
        }}
        
        .btn-secondary {{
            background: #e2e8f0;
            color: #475569;
        }}
        
        .btn-secondary:hover {{
            background: #cbd5e0;
        }}
        
        .btn-success {{
            background: #10b981;
            color: white;
        }}
        
        .btn-success:hover {{
            background: #059669;
        }}
        
        .btn-outline-primary {{
            background: transparent;
            color: #667eea;
            border: 1px solid #667eea;
        }}
        
        .btn-outline-primary:hover {{
            background: #667eea;
            color: white;
        }}
        
        .optimization-progress {{
            margin: 24px 0;
            text-align: center;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 12px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .progress-text {{
            font-size: 14px;
            color: #475569;
            margin: 0;
        }}
        
        .optimization-result {{
            margin: 24px 0;
            padding: 24px;
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            text-align: center;
        }}
        
        .result-success h4 {{
            margin: 0 0 16px 0;
            color: #166534;
        }}
        
        .result-stats {{
            margin: 16px 0;
            padding: 16px;
            background: white;
            border-radius: 6px;
            font-size: 14px;
            color: #374151;
            text-align: left;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        
        .stat-row:last-child {{
            margin-bottom: 0;
            font-weight: 600;
            color: #059669;
        }}
        
        .result-actions {{
            margin: 20px 0;
            display: flex;
            gap: 12px;
            justify-content: center;
        }}
        
        .result-warning {{
            font-size: 12px;
            color: #dc2626;
            margin: 16px 0 0 0;
        }}
        
        .optimization-error {{
            margin: 24px 0;
            padding: 24px;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            text-align: center;
        }}
        
        .error-content h4 {{
            margin: 0 0 12px 0;
            color: #dc2626;
        }}
        
        .error-message {{
            color: #991b1b;
            margin: 0 0 20px 0;
        }}
        
        .optimizer-tips {{
            margin: 24px 0 0 0;
            padding: 20px;
            background: #fffbeb;
            border: 1px solid #fed7aa;
            border-radius: 8px;
        }}
        
        .optimizer-tips h5 {{
            margin: 0 0 12px 0;
            color: #92400e;
            font-size: 16px;
        }}
        
        .optimizer-tips ul {{
            margin: 0;
            padding-left: 20px;
            color: #92400e;
        }}
        
        .optimizer-tips li {{
            margin-bottom: 8px;
        }}
        
        @media (max-width: 600px) {{
            .megahub-tool {{
                margin: 10px;
                max-width: none;
            }}
            
            .limits-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .optimizer-actions {{
                flex-direction: column;
            }}
            
            .result-actions {{
                flex-direction: column;
            }}
        }}
        </style>

        <script>
        (function() {{
            const API_BASE = '/public-tools/file/compressor';
            let selectedFile = null;
            let optimizationId = null;
            let statusCheckInterval = null;
            
            // Éléments DOM
            const fileDropZone = document.getElementById('fileDropZone');
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const selectedFileDiv = document.getElementById('selectedFile');
            const optimizerOptions = document.getElementById('optimizerOptions');
            const resizeEnabled = document.getElementById('resizeEnabled');
            const resizeOptions = document.getElementById('resizeOptions');
            const optimizeBtn = document.getElementById('optimizeBtn');
            const clearBtn = document.getElementById('clearBtn');
            const optimizationProgress = document.getElementById('optimizationProgress');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const optimizationResult = document.getElementById('optimizationResult');
            const resultStats = document.getElementById('resultStats');
            const downloadLink = document.getElementById('downloadLink');
            const newOptimizationBtn = document.getElementById('newOptimizationBtn');
            const optimizationError = document.getElementById('optimizationError');
            const errorMessage = document.getElementById('errorMessage');
            const retryBtn = document.getElementById('retryBtn');
            
            // Event listeners
            fileDropZone.addEventListener('click', () => fileInput.click());
            fileDropZone.addEventListener('dragover', handleDragOver);
            fileDropZone.addEventListener('dragleave', handleDragLeave);
            fileDropZone.addEventListener('drop', handleDrop);
            fileInput.addEventListener('change', handleFileSelect);
            resizeEnabled.addEventListener('change', toggleResizeOptions);
            optimizeBtn.addEventListener('click', startOptimization);
            clearBtn.addEventListener('click', clearFile);
            newOptimizationBtn.addEventListener('click', resetForm);
            retryBtn.addEventListener('click', resetForm);
            
            function handleDragOver(e) {{
                e.preventDefault();
                fileDropZone.classList.add('drag-over');
            }}
            
            function handleDragLeave(e) {{
                e.preventDefault();
                fileDropZone.classList.remove('drag-over');
            }}
            
            function handleDrop(e) {{
                e.preventDefault();
                fileDropZone.classList.remove('drag-over');
                const files = Array.from(e.dataTransfer.files);
                if (files.length > 0) {{
                    selectFile(files[0]);
                }}
            }}
            
            function handleFileSelect(e) {{
                const files = Array.from(e.target.files);
                if (files.length > 0) {{
                    selectFile(files[0]);
                }}
            }}
            
            function selectFile(file) {{
                // Validation du fichier
                const maxSize = {quota.MAX_FILE_SIZE};
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf'];
                
                if (file.size > maxSize) {{
                    showError(`Fichier trop volumineux (max: ${{maxSize / 1024 / 1024}}MB)`);
                    return;
                }}
                
                if (!allowedTypes.includes(file.type)) {{
                    showError('Type de fichier non supporté. Formats acceptés: PDF, JPG, PNG, WebP');
                    return;
                }}
                
                selectedFile = file;
                updateFileDisplay();
                fileInput.value = ''; // Reset input
            }}
            
            function updateFileDisplay() {{
                if (!selectedFile) {{
                    fileInfo.style.display = 'none';
                    optimizerOptions.style.display = 'none';
                    optimizeBtn.disabled = true;
                    clearBtn.style.display = 'none';
                    return;
                }}
                
                // Affichage du fichier
                fileInfo.style.display = 'block';
                optimizerOptions.style.display = 'block';
                clearBtn.style.display = 'inline-flex';
                
                // Masquer les options de redimensionnement pour PDF
                const isImage = selectedFile.type.startsWith('image/');
                document.querySelector('label[for="resizeEnabled"]').parentElement.style.display = 
                    isImage ? 'block' : 'none';
                
                selectedFileDiv.innerHTML = `
                    <div class="file-details">
                        <div class="file-name">${{selectedFile.name}}</div>
                        <div class="file-meta">
                            ${{selectedFile.type}} • ${{formatFileSize(selectedFile.size)}}
                        </div>
                    </div>
                    <button class="file-remove" onclick="clearFile()">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                
                optimizeBtn.disabled = false;
            }}
            
            function toggleResizeOptions() {{
                resizeOptions.style.display = resizeEnabled.checked ? 'block' : 'none';
            }}
            
            function clearFile() {{
                selectedFile = null;
                updateFileDisplay();
            }}
            
            function formatFileSize(bytes) {{
                if (bytes === 0) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
            }}
            
            async function startOptimization() {{
                try {{
                    optimizeBtn.disabled = true;
                    optimizationProgress.style.display = 'block';
                    optimizationResult.style.display = 'none';
                    optimizationError.style.display = 'none';
                    
                    // Préparation des données
                    const formData = new FormData();
                    formData.append('file', selectedFile);
                    formData.append('quality_level', document.getElementById('qualityLevel').value);
                    
                    if (resizeEnabled.checked && document.getElementById('maxDimension').value) {{
                        formData.append('resize_enabled', 'true');
                        formData.append('target_max_dimension', document.getElementById('maxDimension').value);
                    }}
                    
                    updateProgress(10, 'Upload du fichier...');
                    
                    // Envoi de la demande
                    const response = await fetch(`${{API_BASE}}/process/`, {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (!response.ok) {{
                        throw new Error(data.error || 'Erreur d\\'optimisation');
                    }}
                    
                    optimizationId = data.optimization_id;
                    updateProgress(20, 'Optimisation en cours...');
                    
                    // Démarrage du suivi de statut
                    startStatusCheck();
                    
                }} catch (error) {{
                    showError(error.message);
                    optimizeBtn.disabled = false;
                }}
            }}
            
            function startStatusCheck() {{
                statusCheckInterval = setInterval(async () => {{
                    try {{
                        const response = await fetch(`${{API_BASE}}/status/${{optimizationId}}/`);
                        const data = await response.json();
                        
                        if (data.status === 'completed') {{
                            clearInterval(statusCheckInterval);
                            showSuccess(data);
                        }} else if (data.status === 'failed') {{
                            clearInterval(statusCheckInterval);
                            showError(data.error_message || 'Erreur d\\'optimisation');
                        }} else if (data.status === 'processing') {{
                            updateProgress(50, 'Optimisation en cours...');
                        }}
                        
                    }} catch (error) {{
                        console.error('Erreur vérification statut:', error);
                    }}
                }}, 2000);
            }}
            
            function updateProgress(percentage, text) {{
                progressFill.style.width = percentage + '%';
                progressText.textContent = text;
            }}
            
            function showSuccess(data) {{
                optimizationProgress.style.display = 'none';
                optimizationResult.style.display = 'block';
                
                const originalSize = data.original_size;
                const optimizedSize = data.optimized_size;
                const reduction = data.size_reduction_percentage;
                const savedBytes = originalSize - optimizedSize;
                
                resultStats.innerHTML = `
                    <div class="stat-row">
                        <span>Fichier original:</span>
                        <span>${{formatFileSize(originalSize)}}</span>
                    </div>
                    <div class="stat-row">
                        <span>Fichier optimisé:</span>
                        <span>${{formatFileSize(optimizedSize)}}</span>
                    </div>
                    <div class="stat-row">
                        <span>Temps d'optimisation:</span>
                        <span>${{data.optimization_time.toFixed(1)}}s</span>
                    </div>
                    <div class="stat-row">
                        <span>Économie réalisée:</span>
                        <span>${{formatFileSize(savedBytes)}} (-${{reduction.toFixed(1)}}%)</span>
                    </div>
                `;
                
                downloadLink.href = `/public-tools/file/compressor/download/${{data.download_token}}/`;
                downloadLink.download = data.optimized_filename;
            }}
            
            function showError(message) {{
                optimizationProgress.style.display = 'none';
                optimizationError.style.display = 'block';
                errorMessage.textContent = message;
                optimizeBtn.disabled = false;
                
                if (statusCheckInterval) {{
                    clearInterval(statusCheckInterval);
                }}
            }}
            
            function resetForm() {{
                clearFile();
                optimizationProgress.style.display = 'none';
                optimizationResult.style.display = 'none';
                optimizationError.style.display = 'none';
                optimizationId = null;
                
                if (statusCheckInterval) {{
                    clearInterval(statusCheckInterval);
                }}
                
                optimizeBtn.disabled = true;
            }}
            
            // Exposition des fonctions globales
            window.clearFile = clearFile;
            
        }})();
        </script>
        '''
        
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        logger.error(f"Erreur rendu optimiseur: {str(e)}")
        return JsonResponse({'error': 'Erreur de rendu'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_compression(request):
    """Traitement d'une demande d'optimisation publique"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Récupération du fichier
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)
        
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
        
        # Validation de la demande
        service = PublicOptimizationService()
        is_valid, error_message = service.validate_optimization_request(ip_address, file_data)
        
        if not is_valid:
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
        
        # Sauvegarde temporaire du fichier
        temp_upload_dir = os.path.join(
            settings.MEDIA_ROOT, 'temp', 'uploads', str(optimization.id)
        )
        os.makedirs(temp_upload_dir, exist_ok=True)
        
        file_path = os.path.join(temp_upload_dir, uploaded_file.name)
        with open(file_path, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
        
        # Lancement de la tâche d'optimisation
        optimize_public_file_task.delay(str(optimization.id))
        
        return JsonResponse({
            'status': 'success',
            'optimization_id': str(optimization.id),
            'message': 'Optimisation démarrée'
        })
        
    except Exception as e:
        logger.error(f"Erreur traitement optimisation: {str(e)}")
        return JsonResponse({'error': 'Erreur de traitement'}, status=500)

@require_http_methods(["GET"])
def compression_status(request, compression_id):
    """Vérification du statut d'une optimisation"""
    try:
        optimization = PublicFileOptimization.objects.get(id=compression_id)
        
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
        return JsonResponse({'error': 'Optimisation non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur statut optimisation: {str(e)}")
        return JsonResponse({'error': 'Erreur de statut'}, status=500)

@require_http_methods(["GET"])
def download_compressed_file(request, download_token):
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