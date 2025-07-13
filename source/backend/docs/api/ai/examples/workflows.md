# 🚀 AI Infrastructure - Workflows d'Intégration

## Vue d'Ensemble

Cette documentation présente des **workflows concrets** pour intégrer l'infrastructure AI MEGAHUB dans vos applications. Exemples pratiques, code complet et patterns éprouvés.

---

## 🎯 Workflow 1 : Chat Completion Simple

### Cas d'Usage
Générer du contenu SEO (titres, meta descriptions, contenu) via conversation simple.

### Code Frontend (React)
```javascript
// services/aiService.js
import { apiClient } from '@/services/core'

export const aiService = {
  async createChatCompletion(messages, options = {}) {
    const response = await apiClient.post('/ai/openai/chat/', {
      messages,
      model: options.model || 'gpt-4o',
      max_tokens: options.maxTokens || 500,
      temperature: options.temperature || 0.3,
      description: options.description || 'Génération contenu SEO'
    })
    
    return response.data
  },
  
  async getJobResult(jobId) {
    const response = await apiClient.get(
      `/ai/openai/completion/job_result/?job_id=${jobId}`
    )
    return response.data
  }
}

// components/SEOContentGenerator.jsx
import React, { useState } from 'react'
import { aiService } from '@/services/aiService'

export const SEOContentGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const handleGenerate = async () => {
    setLoading(true)
    try {
      const messages = [
        {
          role: 'system',
          content: 'Tu es un expert SEO. Génère du contenu optimisé pour le référencement.'
        },
        {
          role: 'user', 
          content: prompt
        }
      ]
      
      const response = await aiService.createChatCompletion(messages, {
        description: 'Génération contenu SEO',
        temperature: 0.3,
        maxTokens: 300
      })
      
      if (response.status === 'completed') {
        setResult(response.result.completion)
      } else {
        // Job asynchrone, poller le résultat
        const jobId = response.job_id
        setTimeout(() => pollResult(jobId), 2000)
      }
    } catch (error) {
      console.error('Erreur génération:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const pollResult = async (jobId) => {
    try {
      const response = await aiService.getJobResult(jobId)
      if (response.job.status === 'completed') {
        setResult(response.result.completion)
      } else if (response.job.status === 'failed') {
        console.error('Job échoué:', response.error)
      } else {
        // Continuer polling
        setTimeout(() => pollResult(jobId), 2000)
      }
    } catch (error) {
      console.error('Erreur polling:', error)
    }
  }
  
  return (
    <div className="seo-generator">
      <h3>Générateur de Contenu SEO</h3>
      
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Décrivez le contenu à générer..."
        rows={4}
        className="w-full p-3 border rounded"
      />
      
      <button
        onClick={handleGenerate}
        disabled={loading || !prompt.trim()}
        className="mt-3 px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {loading ? 'Génération...' : 'Générer'}
      </button>
      
      {result && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <h4>Résultat généré :</h4>
          <p className="whitespace-pre-wrap">{result}</p>
        </div>
      )}
    </div>
  )
}
```

---

## 📊 Workflow 2 : Analyse Batch avec Monitoring

### Cas d'Usage
Analyser plusieurs contenus en batch avec suivi de progression et coûts.

### Code Backend (Django Service)
```python
# services/batch_analysis_service.py
from ai_core.models import AIJob, AIJobType
from ai_openai.models import OpenAIJob
from ai_usage.services import UsageService
from ai_providers.services import CredentialService, QuotaService
import uuid

class BatchAnalysisService:
    def __init__(self, brand, user):
        self.brand = brand
        self.user = user
        self.company = brand.company if hasattr(brand, 'company') else user.company
    
    def analyze_content_batch(self, contents, analysis_type='seo_analysis'):
        """
        Analyse plusieurs contenus en batch
        """
        # Vérifier credentials OpenAI
        api_key = CredentialService.get_api_key_for_provider(
            self.company, 'openai'
        )
        if not api_key:
            raise ValueError("Clé OpenAI non configurée")
        
        # Estimer coût total
        estimated_tokens = sum(len(content.split()) * 1.3 for content in contents)
        estimated_cost = estimated_tokens * 0.00001  # Estimation grossière
        
        # Vérifier quota
        can_proceed = QuotaService.consume_quota(
            self.company, 'openai', estimated_tokens, estimated_cost
        )
        if not can_proceed:
            raise ValueError("Quota OpenAI insuffisant")
        
        # Créer job type si nécessaire
        job_type, _ = AIJobType.objects.get_or_create(
            name=analysis_type,
            defaults={
                'description': 'Analyse de contenu par lots',
                'category': 'analysis',
                'estimated_duration_seconds': 60,
                'requires_async': True
            }
        )
        
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        results = []
        
        for i, content in enumerate(contents):
            # Créer AIJob central
            ai_job = AIJob.objects.create(
                job_id=f"{batch_id}_item_{i}",
                job_type=job_type,
                brand=self.brand,
                created_by=self.user,
                description=f"Analyse contenu {i+1}/{len(contents)}",
                priority='normal',
                input_data={
                    'content': content,
                    'analysis_type': analysis_type,
                    'batch_id': batch_id,
                    'item_index': i
                }
            )
            
            # Créer OpenAIJob associé
            openai_job = OpenAIJob.objects.create(
                ai_job=ai_job,
                model='gpt-4o',
                temperature=0.1,  # Déterministe pour analyses
                max_tokens=800,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert SEO. Analyse le contenu fourni."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyse SEO de ce contenu:\n\n{content}"
                    }
                ]
            )
            
            results.append({
                'job_id': ai_job.job_id,
                'openai_job_id': openai_job.id,
                'content_preview': content[:100] + '...' if len(content) > 100 else content
            })
        
        return {
            'batch_id': batch_id,
            'total_jobs': len(contents),
            'jobs': results,
            'estimated_cost': estimated_cost,
            'estimated_tokens': estimated_tokens
        }
    
    def get_batch_status(self, batch_id):
        """
        Récupère le statut d'un batch
        """
        jobs = AIJob.objects.filter(
            input_data__batch_id=batch_id,
            brand=self.brand
        ).select_related('openai_job', 'usage')
        
        total = jobs.count()
        completed = jobs.filter(status='completed').count()
        failed = jobs.filter(status='failed').count()
        running = jobs.filter(status='running').count()
        
        # Calculer coût total
        total_cost = sum(
            job.usage.total_cost for job in jobs 
            if hasattr(job, 'usage')
        )
        
        return {
            'batch_id': batch_id,
            'total_jobs': total,
            'completed': completed,
            'failed': failed,
            'running': running,
            'pending': total - completed - failed - running,
            'progress_percentage': (completed / total * 100) if total > 0 else 0,
            'total_cost': str(total_cost),
            'is_complete': completed + failed == total,
            'jobs': [
                {
                    'job_id': job.job_id,
                    'status': job.status,
                    'progress': job.progress_percentage,
                    'cost': str(job.usage.total_cost) if hasattr(job, 'usage') else '0.00',
                    'tokens': job.openai_job.total_tokens if hasattr(job, 'openai_job') else 0
                }
                for job in jobs
            ]
        }
```

### Code Frontend (React Hook)
```javascript
// hooks/useBatchAnalysis.js
import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/services/core'

export const useBatchAnalysis = () => {
  const [batches, setBatches] = useState({})
  const [loading, setLoading] = useState(false)
  
  const startBatchAnalysis = useCallback(async (contents) => {
    setLoading(true)
    try {
      const response = await apiClient.post('/ai/batch-analysis/', {
        contents,
        analysis_type: 'seo_analysis'
      })
      
      const batchId = response.data.batch_id
      setBatches(prev => ({
        ...prev,
        [batchId]: {
          ...response.data,
          status: 'running',
          startedAt: new Date().toISOString()
        }
      }))
      
      // Démarrer polling
      pollBatchStatus(batchId)
      return batchId
    } catch (error) {
      console.error('Erreur démarrage batch:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])
  
  const pollBatchStatus = useCallback(async (batchId) => {
    try {
      const response = await apiClient.get(`/ai/batch-analysis/${batchId}/status/`)
      const batchStatus = response.data
      
      setBatches(prev => ({
        ...prev,
        [batchId]: {
          ...prev[batchId],
          ...batchStatus,
          lastUpdated: new Date().toISOString()
        }
      }))
      
      // Continuer polling si pas terminé
      if (!batchStatus.is_complete) {
        setTimeout(() => pollBatchStatus(batchId), 3000)
      }
    } catch (error) {
      console.error('Erreur polling batch:', error)
    }
  }, [])
  
  const getBatchResults = useCallback(async (batchId) => {
    try {
      const response = await apiClient.get(`/ai/batch-analysis/${batchId}/results/`)
      return response.data
    } catch (error) {
      console.error('Erreur récupération résultats:', error)
      throw error
    }
  }, [])
  
  return {
    batches,
    loading,
    startBatchAnalysis,
    getBatchResults
  }
}

// components/BatchAnalysisManager.jsx
import React, { useState } from 'react'
import { useBatchAnalysis } from '@/hooks/useBatchAnalysis'

export const BatchAnalysisManager = () => {
  const [contents, setContents] = useState([''])
  const { batches, loading, startBatchAnalysis, getBatchResults } = useBatchAnalysis()
  
  const handleAddContent = () => {
    setContents([...contents, ''])
  }
  
  const handleUpdateContent = (index, value) => {
    const newContents = [...contents]
    newContents[index] = value
    setContents(newContents)
  }
  
  const handleStartAnalysis = async () => {
    const validContents = contents.filter(c => c.trim())
    if (validContents.length === 0) return
    
    try {
      await startBatchAnalysis(validContents)
      // Reset form
      setContents([''])
    } catch (error) {
      alert('Erreur lors du démarrage de l\'analyse')
    }
  }
  
  const handleDownloadResults = async (batchId) => {
    try {
      const results = await getBatchResults(batchId)
      // Traiter et télécharger les résultats
      console.log('Résultats:', results)
    } catch (error) {
      alert('Erreur lors de la récupération des résultats')
    }
  }
  
  return (
    <div className="batch-analysis-manager">
      <h2>Analyse de Contenu en Lot</h2>
      
      {/* Formulaire d'ajout */}
      <div className="content-inputs">
        {contents.map((content, index) => (
          <textarea
            key={index}
            value={content}
            onChange={(e) => handleUpdateContent(index, e.target.value)}
            placeholder={`Contenu ${index + 1}...`}
            rows={3}
            className="w-full p-2 border rounded mb-2"
          />
        ))}
        
        <div className="flex gap-2 mb-4">
          <button
            onClick={handleAddContent}
            className="px-3 py-1 bg-gray-500 text-white rounded"
          >
            + Ajouter Contenu
          </button>
          
          <button
            onClick={handleStartAnalysis}
            disabled={loading || contents.every(c => !c.trim())}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            {loading ? 'Démarrage...' : 'Analyser le Lot'}
          </button>
        </div>
      </div>
      
      {/* Suivi des batches */}
      <div className="batches-status">
        <h3>Analyses en Cours</h3>
        {Object.entries(batches).map(([batchId, batch]) => (
          <div key={batchId} className="batch-item p-4 border rounded mb-3">
            <div className="flex justify-between items-center mb-2">
              <h4>Batch {batchId}</h4>
              <span className="text-sm text-gray-500">
                Coût: ${batch.total_cost || '0.00'}
              </span>
            </div>
            
            <div className="progress-bar bg-gray-200 rounded h-2 mb-2">
              <div
                className="bg-blue-500 h-2 rounded transition-all"
                style={{ width: `${batch.progress_percentage || 0}%` }}
              />
            </div>
            
            <div className="flex justify-between text-sm">
              <span>
                {batch.completed || 0}/{batch.total_jobs || 0} terminés
              </span>
              <span>
                {batch.failed || 0} échecs
              </span>
            </div>
            
            {batch.is_complete && (
              <button
                onClick={() => handleDownloadResults(batchId)}
                className="mt-2 px-3 py-1 bg-green-500 text-white rounded text-sm"
              >
                Télécharger Résultats
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 💰 Workflow 3 : Monitoring Usage & Alertes

### Cas d'Usage
Dashboard temps réel des coûts IA avec alertes automatiques.

### Code Frontend (React)
```javascript
// hooks/useUsageMonitoring.js
import { useState, useEffect } from 'react'
import { apiClient } from '@/services/core'

export const useUsageMonitoring = () => {
  const [dashboard, setDashboard] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadDashboard()
    loadAlerts()
    
    // Refresh toutes les 30 secondes
    const interval = setInterval(() => {
      loadDashboard()
      loadAlerts()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])
  
  const loadDashboard = async () => {
    try {
      const response = await apiClient.get('/ai/usage/dashboard/?days=7')
      setDashboard(response.data)
    } catch (error) {
      console.error('Erreur dashboard:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const loadAlerts = async () => {
    try {
      const response = await apiClient.get('/ai/alerts/active/')
      setAlerts(response.data.alerts || [])
    } catch (error) {
      console.error('Erreur alertes:', error)
    }
  }
  
  const checkNewAlerts = async () => {
    try {
      const response = await apiClient.post('/ai/alerts/check_alerts/')
      if (response.data.new_alerts_count > 0) {
        loadAlerts() // Reload alerts
        return response.data.new_alerts
      }
    } catch (error) {
      console.error('Erreur vérification alertes:', error)
    }
    return []
  }
  
  const resolveAlert = async (alertId) => {
    try {
      await apiClient.put(`/ai/alerts/${alertId}/resolve/`)
      loadAlerts() // Reload
    } catch (error) {
      console.error('Erreur résolution alerte:', error)
    }
  }
  
  return {
    dashboard,
    alerts