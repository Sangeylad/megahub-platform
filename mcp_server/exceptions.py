# mcp_server/exceptions.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MCPException(Exception):
    """Exception custom pour MCP avec codes d'erreur"""
    
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class AuthenticationError(MCPException):
    """Erreur d'authentification"""
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")

class ToolNotFoundError(MCPException):
    """Outil non trouvé"""
    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' not found", "TOOL_NOT_FOUND")

class ValidationError(MCPException):
    """Erreur de validation des paramètres"""
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, "VALIDATION_ERROR", details)

def format_error_response(tool_name: str, error: str) -> str:
    """Formate une réponse d'erreur standardisée"""
    return f"❌ **{tool_name}** failed\n\n**Error:** {error}"

def handle_django_error(func_name: str, error: Exception) -> dict:
    """Gère les erreurs Django avec contexte"""
    error_msg = str(error)
    
    # Erreurs courantes Django
    if "does not exist" in error_msg:
        return {
            'success': False,
            'error': f"Resource not found in {func_name}",
            'error_type': 'NOT_FOUND'
        }
    elif "Forbidden" in error_msg or "permission" in error_msg.lower():
        return {
            'success': False,
            'error': f"Access denied in {func_name}",
            'error_type': 'FORBIDDEN'
        }
    elif "Database" in error_msg or "connection" in error_msg.lower():
        return {
            'success': False,
            'error': f"Database error in {func_name}",
            'error_type': 'DATABASE_ERROR'
        }
    else:
        logger.error(f"Unhandled Django error in {func_name}: {error_msg}", exc_info=True)
        return {
            'success': False,
            'error': f"Internal error in {func_name}: {error_msg}",
            'error_type': 'INTERNAL_ERROR'
        }