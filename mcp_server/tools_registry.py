# mcp_server/tools_registry.py
import asyncio
from typing import Dict, Any, List, Callable
from asgiref.sync import sync_to_async

from exceptions import ToolNotFoundError, handle_django_error

class ToolRegistry:
    """Registry centralisé pour tous les outils MCP"""
    
    def __init__(self):
        self._tools = {}
        self._handlers = {}
        self._load_tools()
    
    def _load_tools(self):
        """Charge tous les outils disponibles"""
        try:
            # Import des tools (même niveau)
            from cocoon_tools import COCOON_TOOLS, handle_cocoon_tool
            from keyword_tools import KEYWORD_TOOLS, handle_keyword_tool  
            from website_tools import WEBSITE_TOOLS, handle_website_tool
            
            # Enregistrer les outils
            self._register_tools('cocoon', COCOON_TOOLS, handle_cocoon_tool)
            self._register_tools('keyword', KEYWORD_TOOLS, handle_keyword_tool)
            self._register_tools('website', WEBSITE_TOOLS, handle_website_tool)
            
            print(f"✅ Loaded {len(self._tools)} MCP tools:")
            for category in ['cocoon', 'keyword', 'website']:
                tools_in_cat = [name for name, info in self._tools.items() if info['category'] == category]
                print(f"  📁 {category}: {len(tools_in_cat)} tools")
            
        except ImportError as e:
            print(f"⚠️ Could not load Django tools: {e}")
            self._load_fallback_tools()
    
    def _load_fallback_tools(self):
        """Tools de base si Django indisponible"""
        fallback_tools = [
            {
                "name": "health_check",
                "description": "Check MCP server health",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "test_connection",
                "description": "Test database connection",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "brand_id": {"type": "integer", "description": "Brand ID"}
                    },
                    "required": ["brand_id"]
                }
            }
        ]
        
        for tool in fallback_tools:
            self._tools[tool['name']] = {
                'category': 'system',
                'metadata': tool,
                'handler': self._handle_fallback_tool
            }
            self._handlers[tool['name']] = self._handle_fallback_tool
    
    def _handle_fallback_tool(self, tool_name: str, arguments: Dict[str, Any], brand_id: int) -> Dict[str, Any]:
        """Handler pour tools système"""
        if tool_name == "health_check":
            return {
                'success': True,
                'result': {
                    'status': 'healthy',
                    'server': 'megahub-mcp-server',
                    'tools_loaded': len(self._tools),
                    'categories': list(set(tool['category'] for tool in self._tools.values()))
                }
            }
        elif tool_name == "test_connection":
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM business_brand")
                    count = cursor.fetchone()[0]
                return {
                    'success': True,
                    'result': {
                        'database': 'connected',
                        'brands_in_db': count,
                        'tested_brand_id': brand_id
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Database connection failed: {str(e)}'
                }
        
        return {'success': False, 'error': f'Unknown system tool: {tool_name}'}
    
    def _register_tools(self, category: str, tools: List[dict], handler: Callable):
        """Enregistre les outils d'une catégorie"""
        for tool in tools:
            tool_name = tool['name']
            self._tools[tool_name] = {
                'category': category,
                'metadata': tool,
                'handler': handler
            }
            self._handlers[tool_name] = handler
    
    def get_all_tools_metadata(self) -> List[Dict[str, Any]]:
        """Retourne les métadonnées de tous les outils"""
        return [tool['metadata'] for tool in self._tools.values()]
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Retourne les outils organisés par catégorie"""
        categories = {}
        for tool_name, tool_info in self._tools.items():
            category = tool_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        return categories
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], brand_id: int) -> Dict[str, Any]:
        """Execute un outil de façon asynchrone"""
        if tool_name not in self._tools:
            raise ToolNotFoundError(tool_name)
        
        handler = self._handlers[tool_name]
        category = self._tools[tool_name]['category']
        
        try:
            # Vérifier si c'est un tool système (déjà prêt pour async)
            if category == 'system':
                result = handler(tool_name, arguments, brand_id)
            else:
                # Wrapper asynchrone pour les handlers Django
                sync_handler = sync_to_async(handler)
                result = await sync_handler(tool_name, arguments, brand_id)
            
            # Standardisation
            if isinstance(result, dict) and 'success' in result:
                return result
            else:
                return {'success': True, 'result': result}
                
        except Exception as e:
            return handle_django_error(f"{category}.{tool_name}", e)
    
    def tool_exists(self, tool_name: str) -> bool:
        return tool_name in self._tools
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self._tools:
            raise ToolNotFoundError(tool_name)
        return self._tools[tool_name]