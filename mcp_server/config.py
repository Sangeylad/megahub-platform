# mcp_server/config.py
import os
from dataclasses import dataclass

@dataclass
class MCPConfig:
    # Django
    django_settings_module: str = 'django_app.settings'
    backend_path: str = '/app'  # Dans le container
    
    # Database (héritée du container backend)
    postgres_db: str = os.getenv('POSTGRES_DB', 'mhdb24')
    postgres_user: str = os.getenv('POSTGRES_USER', 'SuperAdminduTurfu')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD', 'MHub2401!')
    postgres_host: str = os.getenv('POSTGRES_HOST', 'postgres')
    
    # MCP Server
    server_name: str = 'megahub-seo-analyzer'
    server_version: str = '1.0.0'
    protocol_version: str = '2024-11-05'
    
    # Auth
    environment: str = os.getenv('MCP_ENV', 'development')
    default_brand_id: int = int(os.getenv('MCP_DEFAULT_BRAND_ID', '9'))
    
    # Logging
    log_level: str = os.getenv('MCP_LOG_LEVEL', 'INFO')

# Instance globale
config = MCPConfig()