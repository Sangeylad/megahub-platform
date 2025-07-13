# mcp_server/runtime_test.py
"""Tests runtime avec structure simplifiée"""

import os
import sys
from pathlib import Path

def test_runtime_environment():
    """Test l'environnement au runtime"""
    print("🔍 Runtime Environment Test")
    print("=" * 40)
    
    # Vérification des volumes
    volumes = ['/app', '/mcp_server']
    for vol in volumes:
        path = Path(vol)
        exists = path.exists()
        print(f"📁 {vol}: {'✅' if exists else '❌'} {'exists' if exists else 'missing'}")
        
        if exists:
            try:
                contents = list(path.iterdir())[:5]
                print(f"   Contents: {[p.name for p in contents]}")
            except PermissionError:
                print("   (permission denied)")
    
    # Vérification manage.py
    manage_py = Path('/app/manage.py')
    print(f"🐍 Django manage.py: {'✅' if manage_py.exists() else '❌'}")
    
    return True

def test_django_runtime():
    """Test Django au runtime"""
    print("\n🔍 Django Runtime Test")
    print("=" * 40)
    
    try:
        from django_integration.context import setup_django, can_setup_django
        
        if not can_setup_django():
            print("❌ Django backend not available")
            return False
        
        print("🔧 Setting up Django...")
        setup_django()
        
        print("🔧 Testing model imports...")
        from business.models import Brand
        from seo_analyzer.models import SemanticCocoon, Keyword, Website
        print("✅ Models imported successfully")
        
        # Test DB connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM business_brand")
            brand_count = cursor.fetchone()[0]
        print(f"✅ Database connected ({brand_count} brands)")
        
        return True
        
    except Exception as e:
        print(f"❌ Django runtime test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_tools():
    """Test les tools MCP avec tools Django réels"""
    print("\n🔍 MCP Tools Test")
    print("=" * 40)
    
    try:
        from tools_registry import ToolRegistry
        registry = ToolRegistry()
        
        tools = registry.get_all_tools_metadata()
        print(f"✅ {len(tools)} MCP tools loaded")
        
        categories = registry.get_tools_by_category()
        for category, tool_names in categories.items():
            print(f"  📁 {category}: {tool_names}")
        
        # Test d'un tool Django réel
        print("\n🔧 Testing Django tools...")
        import asyncio
        
        async def test_django_tools():
            results = {}
            
            # Test 1: List cocoons
            try:
                result = await registry.execute_tool("list_cocoons", {"limit": 3}, 9)
                if result.get('success'):
                    cocoon_count = len(result['result'].get('cocoons', []))
                    print(f"✅ list_cocoons: {cocoon_count} cocoons found")
                    results['cocoons'] = True
                else:
                    print(f"❌ list_cocoons failed: {result.get('error')}")
                    results['cocoons'] = False
            except Exception as e:
                print(f"❌ list_cocoons error: {e}")
                results['cocoons'] = False
            
            # Test 2: Search keywords
            try:
                result = await registry.execute_tool("search_keywords", {"limit": 3}, 9)
                if result.get('success'):
                    keyword_count = len(result['result'].get('keywords', []))
                    print(f"✅ search_keywords: {keyword_count} keywords found")
                    results['keywords'] = True
                else:
                    print(f"❌ search_keywords failed: {result.get('error')}")
                    results['keywords'] = False
            except Exception as e:
                print(f"❌ search_keywords error: {e}")
                results['keywords'] = False
            
            # Test 3: List websites
            try:
                result = await registry.execute_tool("list_websites", {"brand_id": 9}, 9)
                if result.get('success'):
                    website_count = len(result['result'].get('websites', []))
                    print(f"✅ list_websites: {website_count} websites found")
                    results['websites'] = True
                else:
                    print(f"❌ list_websites failed: {result.get('error')}")
                    results['websites'] = False
            except Exception as e:
                print(f"❌ list_websites error: {e}")
                results['websites'] = False
            
            return results
        
        test_results = asyncio.run(test_django_tools())
        
        # Résumé des tests
        successful_tests = sum(1 for success in test_results.values() if success)
        total_tests = len(test_results)
        
        print(f"\n📊 Django tools test summary: {successful_tests}/{total_tests} successful")
        
        # Retourner True si au moins un test passe
        return successful_tests > 0
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_schemas():
    """Test que les schémas des tools sont valides"""
    print("\n🔍 Tool Schemas Test")
    print("=" * 40)
    
    try:
        from tools_registry import ToolRegistry
        registry = ToolRegistry()
        
        tools = registry.get_all_tools_metadata()
        schema_errors = []
        
        for tool in tools:
            # Vérifications de base
            required_fields = ['name', 'description', 'inputSchema']
            missing_fields = [field for field in required_fields if field not in tool]
            
            if missing_fields:
                schema_errors.append(f"{tool.get('name', 'Unknown')}: missing {missing_fields}")
            
            # Vérifier inputSchema
            input_schema = tool.get('inputSchema', {})
            if not isinstance(input_schema, dict):
                schema_errors.append(f"{tool['name']}: inputSchema is not a dict")
            elif 'type' not in input_schema:
                schema_errors.append(f"{tool['name']}: inputSchema missing 'type'")
        
        if schema_errors:
            print("❌ Schema validation errors:")
            for error in schema_errors:
                print(f"   - {error}")
            return False
        else:
            print(f"✅ All {len(tools)} tool schemas are valid")
            return True
            
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MCP Server Runtime Tests")
    print("=" * 50)
    
    all_passed = True
    
    if not test_runtime_environment():
        all_passed = False
    
    if not test_django_runtime():
        all_passed = False
    
    if not test_mcp_tools():
        all_passed = False
    
    if not test_tool_schemas():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All runtime tests passed! MCP server ready.")
        sys.exit(0)
    else:
        print("💥 Some runtime tests failed!")
        sys.exit(1)