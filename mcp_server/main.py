# mcp_server/main.py (version corrigée)
import asyncio
import logging
import sys
import threading
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

# Imports MCP
try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print("✅ MCP imports successful")
except ImportError as e:
    print(f"❌ MCP import error: {e}")

# FastAPI pour HTTP API
from fastapi import FastAPI
import uvicorn

from authentication import authenticate_request
from tools_registry import ToolRegistry
from exceptions import MCPException, format_error_response
from config import config

logger = logging.getLogger(__name__)

class MegahubMCPServer:
    def __init__(self):
        # MCP Server
        self.app = Server("megahub-seo-analyzer")
        self.tool_registry = ToolRegistry()
        self.setup_handlers()
        
        # HTTP API
        self.http_app = FastAPI(title="MCP HTTP API")
        self.setup_http_handlers()
    
    def setup_handlers(self):
        """Configure les handlers MCP avec décorateurs officiels"""
        
        @self.app.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
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
    
    def setup_http_handlers(self):
        """Configure les endpoints HTTP"""
        
        @self.http_app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "server": "megahub-mcp-server",
                "tools_loaded": len(self.tool_registry.get_all_tools_metadata()),
                "categories": self.tool_registry.get_tools_by_category()
            }
        
        @self.http_app.get("/tools")
        async def list_tools():
            try:
                tools = self.tool_registry.get_all_tools_metadata()
                return {
                    "success": True,
                    "tools": tools,
                    "count": len(tools),
                    "categories": self.tool_registry.get_tools_by_category()
                }
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return {"success": False, "error": str(e)}
        
        @self.http_app.post("/execute")
        async def execute_tool(request: dict):
            try:
                tool_name = request.get('tool_name')
                arguments = request.get('arguments', {})
                brand_id = request.get('brand_id')
                
                result = await self.tool_registry.execute_tool(tool_name, arguments, brand_id)
                return result
                
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return {"success": False, "error": str(e)}
    
    def _format_success_response(self, tool_name: str, result: Any) -> str:
        """Formate une réponse de succès"""
        return f"✅ **{tool_name}** executed successfully\n\nResult: {result}"
    
    async def run_http_only(self):
        """Démarre seulement l'API HTTP (pour Docker)"""
        logger.info(f"🚀 Starting MCP HTTP Server on port 8001")
        logger.info(f"Environment: {config.environment}")
        
        tools_count = len(self.tool_registry.get_all_tools_metadata())
        categories = self.tool_registry.get_tools_by_category()
        logger.info(f"Tools available: {tools_count} ({list(categories.keys())})")
        
        # Lancer seulement l'API HTTP
        uvicorn_config = uvicorn.Config(
            self.http_app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
        server = uvicorn.Server(uvicorn_config)
        await server.serve()

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
        
        # En mode Docker : lancer seulement HTTP API
        if config.environment in ['production', 'development']:
            asyncio.run(server.run_http_only())
        else:
            # En mode local : stdio MCP traditionnel
            asyncio.run(server.run())
            
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server crashed: {str(e)}", exc_info=True)
        sys.exit(1)