# backend/shared_services/mcp_bridge.py
import logging
from typing import Dict, Any
from .mcp_client import mcp_client

logger = logging.getLogger(__name__)

class MCPBridge:
    """Bridge pour appeler les tools MCP depuis Django"""
    
    def __init__(self):
        self.client = mcp_client
    
    def health_check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        return self.client.health_check()
    
    def list_tools(self) -> Dict[str, Any]:
        """Liste les tools disponibles"""
        return self.client.list_tools()
    
    def call_tool_sync(self, tool_name: str, arguments: dict, brand_id: int) -> dict:
        """Appel synchrone à un tool MCP via HTTP"""
        try:
            result = self.client.execute_tool(tool_name, arguments, brand_id)
            logger.info(f"MCP tool {tool_name} called successfully")
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Instance globale
mcp_bridge = MCPBridge()