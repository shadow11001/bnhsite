#!/usr/bin/env python3
"""
Test script to validate the hosting plan creation functionality
and category management without needing a live database.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from server import HostingPlan, HostingCategory
from migrate_categories import HOSTING_CATEGORIES, PLAN_TYPE_TO_CATEGORY_KEY
from datetime import datetime
import uuid

def test_models():
    """Test that our models can be instantiated and validated"""
    print("Testing model instantiation...")
    
    # Test HostingCategory model
    category = HostingCategory(
        key="test_category",
        display_name="Test Category",
        description="A test category",
        type="shared",
        sub_type="ssd"
    )
    print(f"✓ HostingCategory created: {category.display_name}")
    
    # Test HostingPlan model
    plan = HostingPlan(
        plan_name="Test Plan",
        plan_type="ssd_shared",
        category_key="ssd_shared",
        base_price=9.99,
        cpu_cores=2,
        memory_gb=4,
        disk_gb=50,
        disk_type="SSD",
        bandwidth="1TB",
        features=["SSL Certificate", "24/7 Support"],
        popular=False,
        markup_percentage=10
    )
    print(f"✓ HostingPlan created: {plan.plan_name} at ${plan.base_price}/mo")

def test_categories():
    """Test the predefined categories"""
    print(f"\nTesting {len(HOSTING_CATEGORIES)} predefined categories...")
    
    for category in HOSTING_CATEGORIES:
        print(f"✓ {category['display_name']} ({category['key']}) - {category['type']}")
        
        # Validate required fields
        required_fields = ['key', 'display_name', 'type', 'is_active', 'display_order']
        for field in required_fields:
            if field not in category or category[field] is None:
                print(f"✗ Missing required field: {field}")
                return False
    
    return True

def test_plan_type_mapping():
    """Test the plan type to category mapping"""
    print(f"\nTesting plan type mapping...")
    
    category_keys = {cat['key'] for cat in HOSTING_CATEGORIES}
    
    for plan_type, category_key in PLAN_TYPE_TO_CATEGORY_KEY.items():
        if category_key not in category_keys:
            print(f"✗ Plan type '{plan_type}' maps to non-existent category '{category_key}'")
            return False
        print(f"✓ {plan_type} -> {category_key}")
    
    return True

def test_api_endpoints():
    """Test that our endpoints are defined correctly"""
    print(f"\nTesting API endpoint definitions...")
    
    # Import the app and check routes
    from server import app
    
    expected_endpoints = [
        ("/api/admin/hosting-plans", "POST"),
        ("/api/admin/hosting-categories", "GET"),
        ("/api/admin/hosting-categories", "POST"),
        ("/api/hosting-categories", "GET"),
    ]
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != 'HEAD':  # Ignore HEAD methods
                    routes.append((route.path, method))
    
    for endpoint, method in expected_endpoints:
        if (endpoint, method) in routes:
            print(f"✓ {method} {endpoint}")
        else:
            print(f"✗ Missing endpoint: {method} {endpoint}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Hosting Plan Creation & Category Management")
    print("=" * 60)
    
    try:
        test_models()
        
        if not test_categories():
            print("❌ Category validation failed")
            return 1
            
        if not test_plan_type_mapping():
            print("❌ Plan type mapping validation failed")
            return 1
            
        if not test_api_endpoints():
            print("❌ API endpoint validation failed")
            return 1
            
        print("\n🎉 All tests passed!")
        print("\n📋 Summary:")
        print(f"  • {len(HOSTING_CATEGORIES)} categories defined")
        print(f"  • {len(PLAN_TYPE_TO_CATEGORY_KEY)} plan type mappings")
        print("  • All required API endpoints present")
        print("  • Models validate successfully")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())