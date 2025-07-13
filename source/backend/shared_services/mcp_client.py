# backend/shared_services/mcp_client.py
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCPClient:
    """Client HTTP pour communiquer avec le MCP server"""
    
    def __init__(self):
        # URL du MCP server dans le réseau Docker
        self.base_url = "http://mcp-server:8001"
        self.session = requests.Session()
        self.session.timeout = 30
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé du MCP server"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def list_tools(self) -> Dict[str, Any]:
        """Liste tous les tools disponibles"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], brand_id: Optional[int] = None) -> Dict[str, Any]:
        """Execute un tool MCP"""
        try:
            payload = {
                "tool_name": tool_name,
                "arguments": arguments,
                "brand_id": brand_id
            }
            
            response = self.session.post(
                f"{self.base_url}/execute",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Instance globale
mcp_client = MCPClient()