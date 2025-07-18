#!/usr/bin/env python3
"""
Backend API Endpoint Validation Script

This script validates that all the required API endpoints exist and are properly configured.
It can be run without a database to check the basic FastAPI setup.
"""

import sys
import inspect
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_fastapi_setup():
    """Test that FastAPI is properly set up with expected endpoints"""
    print("🔍 Testing FastAPI Endpoint Configuration...")
    
    try:
        # Import the FastAPI app
        from server import app, api_router
        print("✅ FastAPI app imported successfully")
        
        # Get all routes from the app
        all_routes = []
        
        # Get routes from the main app
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                all_routes.append({
                    'path': route.path,
                    'methods': list(route.methods),
                    'name': getattr(route, 'name', 'unnamed'),
                    'source': 'main_app'
                })
        
        # Get routes from the API router
        for route in api_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                # API router routes will be prefixed with /api
                full_path = f"/api{route.path}" if not route.path.startswith('/api') else route.path
                all_routes.append({
                    'path': full_path,
                    'methods': list(route.methods),
                    'name': getattr(route, 'name', 'unnamed'),
                    'source': 'api_router'
                })
        
        print(f"📋 Found {len(all_routes)} total routes")
        
        # Check for required endpoints
        required_endpoints = [
            {'path': '/api/admin/hosting-categories', 'method': 'GET', 'desc': 'List categories (admin)'},
            {'path': '/api/admin/hosting-categories', 'method': 'POST', 'desc': 'Create category'},
            {'path': '/api/admin/hosting-plans', 'method': 'GET', 'desc': 'List plans (admin)'},
            {'path': '/api/admin/hosting-plans', 'method': 'POST', 'desc': 'Create plan'},
            {'path': '/api/hosting-plans', 'method': 'GET', 'desc': 'List plans (public)'},
            {'path': '/api/login', 'method': 'POST', 'desc': 'Admin login'},
            {'path': '/api/verify-token', 'method': 'GET', 'desc': 'Verify auth token'},
        ]
        
        print("\n🔍 Checking required endpoints:")
        missing_endpoints = []
        
        for required in required_endpoints:
            found = False
            for route in all_routes:
                if route['path'] == required['path'] and required['method'] in route['methods']:
                    print(f"✅ {required['method']} {required['path']} - {required['desc']}")
                    found = True
                    break
            
            if not found:
                print(f"❌ {required['method']} {required['path']} - {required['desc']} (MISSING)")
                missing_endpoints.append(required)
        
        # List all available endpoints for debugging
        print(f"\n📋 All available endpoints:")
        for route in sorted(all_routes, key=lambda x: x['path']):
            methods_str = ', '.join(sorted(route['methods']))
            print(f"   {methods_str} {route['path']} (from {route['source']})")
        
        if missing_endpoints:
            print(f"\n❌ {len(missing_endpoints)} required endpoints are missing!")
            return False
        else:
            print(f"\n✅ All required endpoints are properly configured!")
            return True
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing FastAPI setup: {e}")
        return False

def test_model_definitions():
    """Test that all required Pydantic models are defined"""
    print("\n🔍 Testing Pydantic Model Definitions...")
    
    try:
        from server import HostingCategory, HostingPlan
        print("✅ HostingCategory model imported")
        print("✅ HostingPlan model imported")
        
        # Test model field definitions
        category_fields = HostingCategory.__fields__.keys()
        plan_fields = HostingPlan.__fields__.keys()
        
        required_category_fields = ['key', 'display_name', 'type', 'is_active']
        required_plan_fields = ['plan_name', 'base_price', 'plan_type']
        
        print(f"📋 HostingCategory fields: {list(category_fields)}")
        print(f"📋 HostingPlan fields: {list(plan_fields)}")
        
        missing_category_fields = [f for f in required_category_fields if f not in category_fields]
        missing_plan_fields = [f for f in required_plan_fields if f not in plan_fields]
        
        if missing_category_fields:
            print(f"❌ Missing HostingCategory fields: {missing_category_fields}")
            return False
        
        if missing_plan_fields:
            print(f"❌ Missing HostingPlan fields: {missing_plan_fields}")
            return False
        
        print("✅ All required model fields are present")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n🔍 Testing Dependencies...")
    
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('motor.motor_asyncio', 'AsyncIOMotorClient'),
        ('pydantic', 'BaseModel'),
        ('uvicorn', 'uvicorn'),
        ('jwt', 'JWT'),
    ]
    
    all_good = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} not available (module: {module})")
            all_good = False
    
    return all_good

def main():
    """Run all validation tests"""
    print("🚀 Blue Nebula Hosting - Backend API Validation")
    print("=" * 55)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Model Definitions", test_model_definitions),
        ("FastAPI Endpoints", test_fastapi_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend API configuration looks good.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)