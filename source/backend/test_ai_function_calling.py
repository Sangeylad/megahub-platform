# backend/test_ai_function_calling.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
django.setup()

from brands_core.models import Brand
from seo_analyzer.services.ai.ai_with_mcp_service import AIWithMCPService

def test_ai_function_calling():
    """Test simple du function calling IA + MCP"""
    
    # Récupérer une brand
    brand = Brand.objects.get(id=1)  # Humari
    
    # Créer le service IA
    ai_service = AIWithMCPService(brand, temperature=0.3)
    
    print(f"🧪 Testing AI function calling with {len(ai_service.mcp_functions)} tools")
    
    # Test simple : demander à l'IA d'explorer
    system_prompt = """Tu es un expert SEO. 
    Utilise les outils disponibles pour explorer les données de la brand.
    Commence par lister les sites web disponibles."""
    
    user_prompt = """Explore les données disponibles pour la brand Humari. 
    Utilise les outils pour me donner un aperçu de la situation actuelle."""
    
    result = ai_service.chat_with_tools(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_iterations=5
    )
    
    print(f"✅ Success: {result.get('success')}")
    print(f"🔄 Iterations: {result.get('total_iterations', 0)}")
    print(f"🛠️ MCP calls: {result.get('mcp_calls_made', 0)}")
    print(f"💬 Final response preview: {result.get('content', '')[:200]}...")
    
    if result.get('mcp_calls_made', 0) > 0:
        print("🎉 Function calling is working!")
    else:
        print("⚠️ No MCP calls made - check tools availability")
    
    return result

if __name__ == "__main__":
    test_ai_function_calling()