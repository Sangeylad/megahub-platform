# backend/test_mcp_bridge.py
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
django.setup()

from shared_services.mcp_client import mcp_client

def test_mcp_integration():
    print("🧪 Testing MCP Bridge from Django...")
    
    # 1. Health check
    print("\n1. Health check...")
    health = mcp_client.health_check()
    print(f"   Status: {health.get('status')}")
    print(f"   Tools: {health.get('tools_loaded')}")
    
    # 2. List tools
    print("\n2. Tools list...")
    tools = mcp_client.list_tools()
    print(f"   Success: {tools.get('success')}")
    print(f"   Count: {tools.get('count')}")
    
    # 3. Execute tool
    print("\n3. Tool execution...")
    result = mcp_client.execute_tool('list_websites', {}, 1)
    print(f"   Success: {result.get('success')}")
    if result.get('success'):
        websites = result.get('result', {}).get('websites', [])
        print(f"   Websites found: {len(websites)}")
        if websites:
            print(f"   First website: {websites[0].get('name')} (ID: {websites[0].get('id')})")
    else:
        print(f"   Error: {result.get('error')}")

if __name__ == "__main__":
    test_mcp_integration()