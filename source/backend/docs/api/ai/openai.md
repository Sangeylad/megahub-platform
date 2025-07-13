# 🟢 AI OpenAI - Intégration OpenAI avec Support O3

## Vue d'Ensemble

L'app `ai_openai` fournit une **intégration spécialisée** avec l'API OpenAI, étendant les jobs IA centraux avec des fonctionnalités avancées : chat completions O3/GPT-4.1, assistants, gestion intelligente des modèles et configurations adaptées par génération.

### Responsabilité
- **OpenAIJob** : Extension des AIJob avec paramètres OpenAI multi-génération
- **Chat Completions** : Interface unifiée pour O3, GPT-4.1 et legacy
- **Auto-Configuration** : Détection automatique des paramètres selon modèle
- **Cost Optimization** : Calcul précis des coûts par modèle
- **Assistant Integration** : Gestion des assistants OpenAI

### Base URL
```
https://backoffice.humari.fr/ai/openai/
```

---

## 🆕 Support Modèles Nouvelle Génération

### Modèles Supportés

#### **O3 Series (Reasoning Models)**
- `o3` : Modèle de raisonnement avancé
- `o3-mini` : Version optimisée coût/performance

**Spécificités O3** :
- ❌ **Pas de temperature** (paramètre non supporté)
- ✅ **reasoning_effort** : `low`, `medium`, `high`
- ✅ **max_completion_tokens** au lieu de `max_tokens`
- ✅ **Messages structurés** automatiques
- ✅ **Role mapping** : `system` → `developer`

#### **GPT-4.1 (Enhanced)**
- `gpt-4.1` : Version améliorée de GPT-4

**Spécificités GPT-4.1** :
- ✅ **temperature** : Défaut 1.0 (plus créatif)
- ✅ **max_completion_tokens** au lieu de `max_tokens`
- ✅ **Messages structurés** automatiques

#### **Legacy Models**
- `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`

**Spécificités Legacy** :
- ✅ **temperature** : Défaut 0.7
- ✅ **max_tokens** classique
- ✅ **Messages simples** (chaînes de caractères)

---

## 📊 Modèles de Données Actualisés

### OpenAIJob (Extended)
```python
# Extension spécialisée pour AIJob
- ai_job: OneToOne → AIJob (relation centrale)

# Config multi-génération
- model: str # "gpt-4o", "o3", "gpt-4.1"
- temperature: float (NULL pour O3) # 0.0-2.0 ou NULL
- max_tokens: int # Legacy seulement
- max_completion_tokens: int # 🆕 O3/GPT-4.1 seulement

# 🆕 PARAMÈTRES O3 SPÉCIFIQUES
- reasoning_effort: str # 'low', 'medium', 'high' pour O3
- messages_format: str # 'legacy', 'structured'

# Tools et response (inchangé)
- tools: JSON # Outils disponibles
- tool_resources: JSON # Resources pour tools
- response_format: JSON # Format de réponse

# Response OpenAI (inchangé)
- openai_id: str # ID completion OpenAI
- completion_tokens: int # Tokens de réponse
- prompt_tokens: int # Tokens de prompt
- total_tokens: int # Total tokens
```

### Nouvelles Propriétés
```python
@property
def is_o3_model(self):
    """Détecte si c'est un modèle O3"""
    return self.model.startswith('o3')

@property  
def is_new_generation_model(self):
    """Détecte modèles nouvelle génération"""
    return self.model.startswith('o3') or self.model in ['gpt-4.1']
```

---

## 🎯 Endpoints Actualisés

### Chat Completions Multi-Modèles

#### `POST /ai/openai/chat/`
**Création de chat completion avec auto-configuration**

**Paramètres Universels** :
```json
{
  "messages": [
    {"role": "user", "content": "Analyse ce contenu SEO..."}
  ],
  "model": "o3",                      // 🆕 Support O3
  "description": "Analyse SEO avec O3",
  "tools": [                          // Optionnel, tous modèles
    {"type": "file_search"}
  ]
}
```

**Paramètres Spécifiques par Modèle** :

#### **Pour O3 Models** :
```json
{
  "model": "o3",
  "reasoning_effort": "high",         // 🆕 REQUIS pour O3
  "max_completion_tokens": 2000,     // 🆕 Au lieu de max_tokens
  "response_format": {"type": "text"}
  // ❌ temperature non supportée
}
```

#### **Pour GPT-4.1** :
```json
{
  "model": "gpt-4.1", 
  "temperature": 1.0,                 // Défaut plus créatif
  "max_completion_tokens": 10000,     // 🆕 Nouvelle limite
  "top_p": 1,
  "frequency_penalty": 0,
  "presence_penalty": 0
}
```

#### **Pour Legacy (GPT-4o, etc.)** :
```json
{
  "model": "gpt-4o",
  "temperature": 0.7,                 // Défaut équilibré
  "max_tokens": 1000,                 // Format classique
  "tools": [...]
}
```

**Auto-Configuration Intelligente** :
- **Détection automatique** du type de modèle
- **Paramètres par défaut** optimisés selon le modèle
- **Conversion automatique** des messages pour nouveaux modèles
- **Validation** des paramètres incompatibles

**Réponse Synchrone** :
```json
{
  "job_id": "ai_job_abc123",
  "status": "completed",
  "result": {
    "completion": "Analyse SEO détaillée...",
    "finish_reason": "stop"
  },
  "usage": {
    "prompt_tokens": 125,
    "completion_tokens": 275,
    "total_tokens": 400,
    "cost_usd": "0.008000"            // 🆕 Coût O3 plus élevé
  },
  "model": "o3",
  "generation": "new",                // 🆕 Indicateur génération
  "reasoning_effort": "high",         // 🆕 Pour O3
  "execution_time_ms": 5200           // 🆕 O3 plus lent mais meilleur
}
```

**Réponse Asynchrone** (jobs complexes) :
```json
{
  "job_id": "ai_job_def456",
  "status": "async",
  "task_id": "celery-task-789",
  "message": "Job started asynchronously with o3",
  "estimated_completion": "2024-12-20T15:05:00Z"
}
```

#### `GET /ai/openai/chat/`
**Modèles disponibles avec spécificités**

**Réponse enrichie** :
```json
{
  "models": [
    {
      "id": "o3",
      "name": "O3",
      "description": "Modèle de raisonnement avancé",
      "generation": "new",
      "supports_reasoning": true,
      "supports_temperature": false,
      "input_cost_per_token": 0.000020,
      "output_cost_per_token": 0.000020,
      "context_window": 200000,
      "recommended_for": ["analysis", "reasoning", "complex_tasks"],
      "default_params": {
        "reasoning_effort": "medium",
        "max_completion_tokens": 1000
      }
    },
    {
      "id": "o3-mini",
      "name": "O3 Mini", 
      "description": "O3 optimisé coût/performance",
      "generation": "new",
      "supports_reasoning": true,
      "supports_temperature": false,
      "input_cost_per_token": 0.000005,
      "output_cost_per_token": 0.000005,
      "context_window": 200000,
      "recommended_for": ["simple_reasoning", "cost_optimization"]
    },
    {
      "id": "gpt-4.1",
      "name": "GPT-4.1",
      "description": "GPT-4 enhanced",
      "generation": "new", 
      "supports_reasoning": false,
      "supports_temperature": true,
      "input_cost_per_token": 0.000004,
      "output_cost_per_token": 0.000004,
      "context_window": 200000,
      "recommended_for": ["creative", "large_context"],
      "default_params": {
        "temperature": 1.0,
        "max_completion_tokens": 10000
      }
    },
    {
      "id": "gpt-4o",
      "name": "GPT-4 Omni",
      "description": "Modèle multimodal équilibré",
      "generation": "legacy",
      "supports_reasoning": false,
      "supports_temperature": true,
      "input_cost_per_token": 0.000002,
      "output_cost_per_token": 0.000002,
      "context_window": 128000,
      "recommended_for": ["general", "multimodal", "cost_effective"],
      "default_params": {
        "temperature": 0.7,
        "max_tokens": 1000
      }
    }
  ],
  "generation_info": {
    "new": {
      "models": ["o3", "o3-mini", "gpt-4.1"],
      "features": ["structured_messages", "max_completion_tokens"],
      "limitations": ["no_temperature_for_o3"]
    },
    "legacy": {
      "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
      "features": ["temperature", "max_tokens", "proven_stability"]
    }
  }
}
```

---

## 🔄 Services Internes Actualisés

### ChatService (Enhanced)

#### Auto-Configuration par Modèle
```python
@staticmethod
def create_chat_job(
    messages: List[Dict],
    brand, created_by,
    model: str = 'gpt-4o',
    temperature: Optional[float] = None,
    reasoning_effort: Optional[str] = None,
    max_completion_tokens: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Auto-configure selon le modèle"""
    
    # 🎯 DÉTECTION GÉNÉRATION
    is_new_gen = model.startswith('o3') or model in ['gpt-4.1']
    
    # 🎯 CONFIGURATION AUTOMATIQUE
    if is_new_gen:
        if model.startswith('o3'):
            # Configuration O3
            config = {
                'reasoning_effort': reasoning_effort or 'medium',
                'temperature': None,  # ❌ Non supporté
                'max_completion_tokens': max_completion_tokens or 1000
            }
        else:
            # Configuration GPT-4.1
            config = {
                'reasoning_effort': None,
                'temperature': temperature or 1.0,
                'max_completion_tokens': max_completion_tokens or 10000
            }
    else:
        # Configuration Legacy
        config = {
            'reasoning_effort': None,
            'temperature': temperature or 0.7,
            'max_tokens': max_completion_tokens or 1000
        }
```

### OpenAIService (Enhanced)

#### Conversion Automatique Messages
```python
def _convert_messages_to_structured(self, messages: List[Dict]) -> List[Dict]:
    """Convertit pour nouveaux modèles"""
    structured_messages = []
    
    for msg in messages:
        role = msg['role']
        content = msg['content']
        
        # 🎯 MAPPING ROLES O3
        if role == 'system':
            role = 'developer'  # O3 utilise 'developer' au lieu de 'system'
        
        # 🎯 STRUCTURE CONTENT
        if isinstance(content, str):
            structured_content = [{"type": "text", "text": content}]
        else:
            structured_content = content
        
        structured_messages.append({
            'role': role,
            'content': structured_content
        })
    
    return structured_messages
```

#### Payload Adaptatif
```python
def _build_payload(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
    """Construit payload selon le modèle"""
    
    is_new_gen = self._is_new_generation_model(model)
    
    # Messages formatés selon génération
    if is_new_gen:
        formatted_messages = self._convert_messages_to_structured(messages)
    else:
        formatted_messages = messages
    
    payload = {"model": model, "messages": formatted_messages}
    
    # 🎯 PARAMÈTRES SELON GÉNÉRATION
    if is_new_gen:
        if model.startswith('o3'):
            # Paramètres O3 spécifiques
            payload["reasoning_effort"] = kwargs.get('reasoning_effort', 'medium')
            if kwargs.get('max_completion_tokens'):
                payload["max_completion_tokens"] = kwargs['max_completion_tokens']
        else:
            # GPT-4.1 paramètres
            payload.update({
                "temperature": kwargs.get('temperature', 1.0),
                "max_completion_tokens": kwargs.get('max_completion_tokens', 10000)
            })
    else:
        # Legacy paramètres
        payload.update({
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 1000)
        })
    
    return payload
```

---

## 💰 Coûts par Modèle (Actualisé 2024)

### Pricing O3 & GPT-4.1
```python
OPENAI_PRICING_2024 = {
    # 🆕 NOUVEAUX MODÈLES
    "o3": {
        "input": 0.000020,    # $20 / 1M tokens (estimation élevée)
        "output": 0.000020,   # $20 / 1M tokens 
        "reasoning_cost": True,  # Coût du raisonnement inclus
        "performance": "highest"
    },
    "o3-mini": {
        "input": 0.000005,    # $5 / 1M tokens
        "output": 0.000005,   # $5 / 1M tokens
        "reasoning_cost": True,
        "performance": "high_efficiency"
    },
    "gpt-4.1": {
        "input": 0.000004,    # $4 / 1M tokens (estimation)
        "output": 0.000004,   # $4 / 1M tokens
        "performance": "enhanced"
    },
    
    # MODÈLES EXISTANTS
    "gpt-4o": {
        "input": 0.000002,    # $2 / 1M tokens
        "output": 0.000002,   # $2 / 1M tokens
        "performance": "balanced"
    },
    "gpt-4-turbo": {
        "input": 0.000003,    # $3 / 1M tokens
        "output": 0.000003,   # $3 / 1M tokens
        "performance": "fast"
    }
}
```

### Calcul Automatique des Coûts
```python
def _get_cost_per_token(model: str) -> float:
    """Calcul précis selon modèle"""
    costs = OPENAI_PRICING_2024.get(model, {})
    
    # Moyenne input/output pour simplicité
    input_cost = costs.get('input', 0.000002)
    output_cost = costs.get('output', 0.000002)
    
    return (input_cost + output_cost) / 2
```

---

## 🚨 Validation et Gestion d'Erreurs

### Validation Spécialisée par Modèle
```python
def validate(self, data):
    """Validation selon le modèle"""
    model = data.get('model', 'gpt-4o')
    
    # 🎯 VALIDATION O3
    if model.startswith('o3'):
        if 'temperature' in data:
            raise ValidationError("O3 models don't support temperature parameter")
        
        if not data.get('reasoning_effort'):
            data['reasoning_effort'] = 'medium'
        
        # Conversion max_tokens → max_completion_tokens
        if 'max_tokens' in data and 'max_completion_tokens' not in data:
            data['max_completion_tokens'] = data.pop('max_tokens')
    
    # 🎯 VALIDATION GPT-4.1
    elif model == 'gpt-4.1':
        if not data.get('temperature'):
            data['temperature'] = 1.0
        
        # Conversion vers max_completion_tokens
        if 'max_tokens' in data:
            data['max_completion_tokens'] = data.pop('max_tokens')
    
    # 🎯 VALIDATION LEGACY
    else:
        if 'reasoning_effort' in data:
            raise ValidationError(f"Model {model} doesn't support reasoning_effort")
        
        if not data.get('temperature'):
            data['temperature'] = 0.7
    
    return data
```

### Erreurs Spécifiques O3
```json
// Temperature sur O3
{
  "error": "O3 models don't support temperature parameter",
  "error_code": "INVALID_PARAMETER_FOR_MODEL",
  "model": "o3",
  "invalid_params": ["temperature"],
  "suggested_params": ["reasoning_effort", "max_completion_tokens"]
}

// Reasoning effort sur legacy
{
  "error": "Model gpt-4o doesn't support reasoning_effort parameter", 
  "error_code": "INVALID_PARAMETER_FOR_MODEL",
  "model": "gpt-4o",
  "invalid_params": ["reasoning_effort"],
  "suggested_params": ["temperature", "max_tokens"]
}
```

---

## 📈 Performance et Monitoring

### Métriques par Génération
```python
# Tracking automatique amélioré
{
  "model": "o3",
  "generation": "new",
  "execution_time_ms": 5200,        # O3 plus lent mais meilleur
  "reasoning_effort": "high",       # Impact sur temps/coût
  "cost_usd": "0.008000",          # Coût élevé O3
  "quality_score": 9.8,            # Qualité supérieure
  "reasoning_steps": 47            # 🆕 Étapes de raisonnement
}
```

### Recommandations Automatiques
```python
def get_model_recommendation(task_complexity: float, budget_constraint: float):
    """Recommandation intelligente de modèle"""
    
    if task_complexity > 0.9 and budget_constraint > 0.7:
        return "o3"  # Tâches complexes, budget confortable
    elif task_complexity > 0.7 and budget_constraint > 0.5:
        return "o3-mini"  # Bon compromis qualité/prix
    elif task_complexity > 0.5:
        return "gpt-4.1"  # Créativité et contexte large
    else:
        return "gpt-4o"  # Tâches standard, économique
```

---

## 🔄 Migration et Compatibilité

### Migration Automatique des Paramètres
```python
# Conversion automatique legacy → new generation
if model.startswith('o3') and 'max_tokens' in params:
    params['max_completion_tokens'] = params.pop('max_tokens')
    del params['temperature']  # Retirer temperature pour O3

if model == 'gpt-4.1' and 'max_tokens' in params:
    params['max_completion_tokens'] = params.pop('max_tokens')
```

### Rétrocompatibilité
- **API legacy** : Continue de fonctionner avec auto-conversion
- **Paramètres legacy** : Convertis automatiquement selon le modèle
- **Réponses** : Format uniforme avec champs additionnels pour nouveaux modèles

---

## 💡 Bonnes Pratiques Mises à Jour

### Choix de Modèle Optimal
1. **O3** : Analyse complexe, raisonnement critique, recherche
2. **O3-mini** : Bon compromis pour tâches de raisonnement courantes
3. **GPT-4.1** : Création de contenu, contexte large, créativité
4. **GPT-4o** : Tâches standard, multimodal, efficacité

### Optimisation des Coûts O3
1. **reasoning_effort = 'low'** pour tâches simples
2. **Batch processing** pour réduire les coûts fixes
3. **Cache intelligent** pour requêtes similaires
4. **Fallback** : O3-mini puis GPT-4o selon budget

### Monitoring Avancé
1. **Tracking par génération** pour analyser ROI
2. **Alertes coût** spécifiques O3 (plus cher)
3. **Métriques qualité** pour justifier surcoût O3
4. **Usage patterns** pour optimisation future

---

**Cette documentation couvre l'intégration OpenAI complète avec support O3/GPT-4.1. L'architecture auto-configure intelligemment selon le modèle choisi, garantissant performances optimales et compatibilité totale.**