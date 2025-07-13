# mcp_server/tools/__init__.py
"""
Tools MCP pour MEGAHUB
Structure modulaire avec fallback graceful
"""

# mcp_server/tools/cocoon_tools.py
"""Tools pour les cocons sémantiques"""

# Outils disponibles
COCOON_TOOLS = [
    {
        "name": "list_cocoons",
        "description": "List all semantic cocoons for a brand",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_cocoon_details", 
        "description": "Get detailed information about a specific cocoon",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "cocoon_id": {"type": "integer", "description": "Cocoon ID"}
            },
            "required": ["brand_id", "cocoon_id"]
        }
    }
]

def handle_cocoon_tool(tool_name: str, arguments: dict, brand_id: int) -> dict:
    """Handler pour les outils cocoon (synchrone)"""
    try:
        # Import Django models ici
        from seo_analyzer.models import SemanticCocoon
        
        if tool_name == "list_cocoons":
            cocoons = SemanticCocoon.objects.all()
            return {
                'success': True,
                'result': {
                    'cocoons': [
                        {
                            'id': cocoon.id,
                            'name': cocoon.name,
                            'description': cocoon.description
                        }
                        for cocoon in cocoons[:10]  # Limite pour test
                    ],
                    'total_count': cocoons.count()
                }
            }
        
        elif tool_name == "get_cocoon_details":
            cocoon_id = arguments.get('cocoon_id')
            try:
                cocoon = SemanticCocoon.objects.get(id=cocoon_id)
                return {
                    'success': True,
                    'result': {
                        'id': cocoon.id,
                        'name': cocoon.name,
                        'description': cocoon.description,
                        'keywords_count': cocoon.cocoon_keywords.count()
                    }
                }
            except SemanticCocoon.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Cocoon {cocoon_id} not found'
                }
        
        else:
            return {
                'success': False,
                'error': f'Unknown cocoon tool: {tool_name}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in {tool_name}: {str(e)}'
        }