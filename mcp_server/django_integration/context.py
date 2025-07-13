# mcp_server/django_integration/context.py
import os
import sys
import django
from pathlib import Path

def setup_django():
    """Configure Django pour MCP avec gestion build/runtime"""
    
    try:
        # Configuration des chemins
        _setup_paths()
        
        # Variables d'environnement
        _setup_environment()
        
        # Initialisation Django sécurisée
        _initialize_django()
        
        print("✅ Django context initialized for MCP server")
        
    except Exception as e:
        print(f"❌ Django setup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def _setup_paths():
    """Configure les chemins Python selon l'environnement"""
    
    # 🎯 DISTINCTION BUILD vs RUNTIME
    is_build_time = not Path('/app').exists()  # Volume pas monté = build time
    
    if is_build_time:
        print("🔧 Build time detected - skipping Django backend path requirement")
        # Au build, on ajoute juste le chemin MCP
        mcp_path = Path(__file__).parent.parent
        sys.path.insert(0, str(mcp_path))
        return
    
    # Runtime : chercher le backend Django
    possible_backend_paths = [
        Path('/app'),                    # Volume mount principal
        Path('/backend'),                # Alternative
        Path('/mcp_server/../backend'),  # Relatif
        Path(__file__).parent.parent.parent / 'backend'  # Local dev
    ]
    
    backend_path = None
    for path in possible_backend_paths:
        if path.exists() and (path / 'manage.py').exists():
            backend_path = path
            break
    
    if not backend_path:
        print("🔍 Available paths at runtime:")
        for path in possible_backend_paths:
            manage_exists = (path / 'manage.py').exists() if path.exists() else False
            print(f"  - {path} (exists: {path.exists()}, manage.py: {manage_exists})")
        
        # Liste du contenu de /app si existe
        app_path = Path('/app')
        if app_path.exists():
            print(f"📁 Contents of /app:")
            try:
                for item in app_path.iterdir():
                    print(f"    - {item.name}")
            except PermissionError:
                print("    - (permission denied)")
        
        raise FileNotFoundError("Django backend not found in any expected location")
    
    print(f"✅ Found Django backend at: {backend_path}")
    sys.path.insert(0, str(backend_path))
    
    # Chemin MCP server
    mcp_path = Path(__file__).parent.parent
    sys.path.insert(0, str(mcp_path))

def _setup_environment():
    """Configure les variables d'environnement Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_integration.settings')
    
    # Variables avec fallbacks
    env_vars = {
        'POSTGRES_DB': 'mhdb24',
        'POSTGRES_USER': 'SuperAdminduTurfu',
        'POSTGRES_PASSWORD': 'MHub2401!',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_PORT': '5432'
    }
    
    for var, default in env_vars.items():
        if var not in os.environ:
            os.environ[var] = default

def _initialize_django():
    """Initialise Django seulement si backend disponible"""
    
    # Skip si build time
    if not Path('/app').exists():
        print("🔧 Build time - skipping Django initialization")
        return
    
    try:
        from django.conf import settings
        
        if settings.configured:
            print("✅ Django already configured")
            return
        
        # Setup Django
        django.setup()
        
        # Test des apps
        from django.apps import apps
        if apps.ready:
            print(f"✅ Django ready with {len(apps.get_app_configs())} apps")
        else:
            print("⚠️ Django apps not fully ready")
        
    except Exception as e:
        print(f"⚠️ Django initialization failed: {e}")
        if os.getenv('MCP_ENV') == 'development':
            print("🔧 Development mode - continuing anyway")
        else:
            raise

def can_setup_django() -> bool:
    """Vérifie si Django peut être configuré"""
    return Path('/app').exists() and (Path('/app') / 'manage.py').exists()