import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

# Configuration Django
try:
    from django_integration.context import setup_django, can_setup_django
    
    if can_setup_django():
        setup_django()
        print("✅ Django configured for MCP")
    else:
        print("⚠️ Django backend not available - running in limited mode")
        
except Exception as e:
    print(f"⚠️ Django setup issue: {e}")
    if __name__ == "__main__":
        sys.exit(1)

# Imports MCP avec syntaxe officielle
try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print("✅ MCP imports successful")
except ImportError as e:
    print(f"❌ MCP import error: {e}")
    if __name__ == "__main__":
        sys.exit(1)

from authentication import authenticate_request
from tools_registry import ToolRegistry
from exceptions import MCPException, format_error_response
from config import config

logger = logging.getLogger(__name__)

class MegahubMCPServer:
    def __init__(self):
        # ✅ Syntaxe officielle
        self.app = Server("megahub-seo-analyzer")
        self.tool_registry = ToolRegistry()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configure les handlers MCP avec décorateurs officiels"""
        
        @self.app.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Liste tous les outils disponibles"""
            try:
                tools_metadata = self.tool_registry.get_all_tools_metadata()
                tools = []
                
                for tool_meta in tools_metadata:
                    tools.append(types.Tool(
                        name=tool_meta["name"],
                        description=tool_meta["description"],
                        inputSchema=tool_meta["inputSchema"]
                    ))
                
                logger.info(f"Listed {len(tools)} tools")
                return tools
                
            except Exception as e:
                logger.error(f"Error listing tools: {str(e)}", exc_info=True)
                raise Exception(f"Failed to list tools: {str(e)}")
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Execute un outil MCP"""
            try:
                logger.info(f"Executing tool: {name}")
                
                # Authentification
                brand_id = await authenticate_request(arguments)
                
                # Exécution
                result = await self.tool_registry.execute_tool(name, arguments, brand_id)
                
                # Formatage
                if result.get('success', False):
                    content = self._format_success_response(name, result['result'])
                else:
                    content = format_error_response(name, result.get('error', 'Unknown error'))
                
                return [types.TextContent(type="text", text=content)]
                
            except Exception as e:
                logger.error(f"Tool error in {name}: {str(e)}", exc_info=True)
                return [types.TextContent(type="text", text=format_error_response(name, str(e)))]
    
    def _format_success_response(self, tool_name: str, result: Any) -> str:
        """Formate une réponse de succès"""
        content = f"✅ **{tool_name}** executed successfully\n\n"
        
        # Métriques rapides
        if isinstance(result, dict):
            metrics = []
            if 'count' in result:
                metrics.append(f"Count: {result['count']}")
            if 'total_count' in result:
                metrics.append(f"Total: {result['total_count']}")
            
            # Compter les listes
            for key in ['cocoons', 'keywords', 'websites', 'pages']:
                if key in result and isinstance(result[key], list):
                    metrics.append(f"{key.title()}: {len(result[key])}")
            
            if metrics:
                content += f"📊 **Metrics:** {' | '.join(metrics)}\n\n"
        
        # JSON formaté et limité
        try:
            json_str = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            if len(json_str) > 2500:
                # Résumé intelligent
                if isinstance(result, dict):
                    summary = {}
                    for key, value in result.items():
                        if isinstance(value, list) and len(value) > 3:
                            summary[key] = {
                                "count": len(value),
                                "sample": value[:3],
                                "truncated": True
                            }
                        else:
                            summary[key] = value
                    json_str = json.dumps(summary, ensure_ascii=False, indent=2, default=str)
                else:
                    json_str = json_str[:2500] + "\n... (truncated)"
            
            content += f"```json\n{json_str}\n```"
        except Exception:
            content += f"\n**Result:** {str(result)[:1000]}"
        
        return content
    
    async def run(self):
        """Démarre le serveur MCP avec syntaxe officielle"""
        logger.info(f"🚀 Starting MEGAHUB MCP Server")
        logger.info(f"Environment: {config.environment}")
        
        tools_count = len(self.tool_registry.get_all_tools_metadata())
        categories = self.tool_registry.get_tools_by_category()
        logger.info(f"Tools available: {tools_count} ({list(categories.keys())})")
        
        try:
            # ✅ Syntaxe officielle
            async with stdio_server() as streams:
                await self.app.run(
                    streams[0], 
                    streams[1], 
                    self.app.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise

def setup_logging():
    """Configure le logging"""
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

if __name__ == "__main__":
    setup_logging()
    
    try:
        server = MegahubMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server crashed: {str(e)}", exc_info=True)
        sys.exit(1)