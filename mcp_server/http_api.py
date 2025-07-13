# mcp_server/http_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from tools_registry import ToolRegistry
from authentication import authenticate_request

logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Tools API", version="1.0.0")

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    brand_id: Optional[int] = None

class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

# Instance globale
tool_registry = ToolRegistry()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tools_loaded": len(tool_registry.get_all_tools_metadata()),
        "categories": tool_registry.get_tools_by_category()
    }

@app.get("/tools")
async def list_tools():
    """Liste tous les tools disponibles"""
    try:
        tools = tool_registry.get_all_tools_metadata()
        return {
            "success": True,
            "tools": tools,
            "count": len(tools),
            "categories": tool_registry.get_tools_by_category()
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute un tool MCP"""
    try:
        # Auth si brand_id fourni
        if request.brand_id:
            brand_id = await authenticate_request(request.arguments)
        else:
            brand_id = request.brand_id

        # Exécution
        result = await tool_registry.execute_tool(
            request.tool_name, 
            request.arguments, 
            brand_id
        )
        
        return ToolResponse(**result)
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return ToolResponse(
            success=False, 
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)