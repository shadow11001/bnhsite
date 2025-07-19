#!/usr/bin/env python3
"""
Test script to validate the bidirectional field mapping for hosting plans
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from server import map_hosting_plan_fields

def test_old_database_schema_to_frontend():
    """Test mapping from old database schema (name, type, price) to frontend"""
    old_plan = {
        "id": "test-id-1",
        "name": "Test Plan",
        "type": "ssd_shared", 
        "price": 9.99,
        "sub_type": "ssd",
        "popular": True,
        "features": ["SSD Storage", "cPanel"]
    }
    
    mapped = map_hosting_plan_fields(old_plan, to_frontend=True)
    
    # Should return consistent frontend format
    assert mapped["name"] == "Test Plan"
    assert mapped["type"] == "ssd_shared"
    assert mapped["price"] == 9.99
    assert mapped["is_popular"] == True
    assert mapped["sub_type"] == "ssd"
    
    print("✅ Old database schema to frontend mapping: PASSED")

def test_new_database_schema_to_frontend():
    """Test mapping from new database schema (plan_name, plan_type, base_price) to frontend"""
    new_plan = {
        "id": "test-id-2",
        "plan_name": "Test Plan 2",
        "plan_type": "hdd_shared",
        "base_price": 5.99,
        "popular": False,
        "features": ["HDD Storage", "cPanel"]
    }
    
    mapped = map_hosting_plan_fields(new_plan, to_frontend=True)
    
    # Should return consistent frontend format
    assert mapped["name"] == "Test Plan 2"
    assert mapped["type"] == "hdd_shared"
    assert mapped["price"] == 5.99
    assert mapped["is_popular"] == False
    
    print("✅ New database schema to frontend mapping: PASSED")

def test_frontend_to_database_mapping():
    """Test mapping from frontend format to database format"""
    frontend_plan = {
        "name": "Frontend Plan",
        "type": "standard_vps",
        "price": 19.99,
        "is_popular": True,
        "cpu_cores": 2,
        "memory_gb": 4
    }
    
    mapped = map_hosting_plan_fields(frontend_plan, to_frontend=False)
    
    # Should return database format with new schema field names
    assert mapped["plan_name"] == "Frontend Plan"
    assert mapped["plan_type"] == "standard_vps"
    assert mapped["base_price"] == 19.99
    assert mapped["popular"] == True
    assert mapped["cpu_cores"] == 2
    assert mapped["memory_gb"] == 4
    
    print("✅ Frontend to database mapping: PASSED")

def test_mixed_schema_handling():
    """Test handling of mixed schema where some fields use old names, some use new"""
    mixed_plan = {
        "id": "test-id-3",
        "plan_name": "Mixed Plan",  # New schema
        "type": "performance_vps",  # Old schema
        "base_price": 39.99,        # New schema
        "popular": True,            # Database schema
        "cpu_cores": 4
    }
    
    mapped = map_hosting_plan_fields(mixed_plan, to_frontend=True)
    
    # Should handle mixed schemas gracefully
    assert mapped["name"] == "Mixed Plan"
    assert mapped["type"] == "performance_vps"
    assert mapped["price"] == 39.99
    assert mapped["is_popular"] == True
    
    print("✅ Mixed schema handling: PASSED")

def test_empty_plan_handling():
    """Test handling of empty or None plans"""
    assert map_hosting_plan_fields(None, to_frontend=True) is None
    assert map_hosting_plan_fields({}, to_frontend=True) == {}
    
    print("✅ Empty plan handling: PASSED")

def test_popular_field_defaults():
    """Test that popular field defaults are handled correctly"""
    plan_without_popular = {
        "name": "Default Popular Test",
        "type": "standard_gameserver",
        "price": 15.99
    }
    
    mapped = map_hosting_plan_fields(plan_without_popular, to_frontend=True)
    assert mapped["is_popular"] == False  # Should default to False
    
    print("✅ Popular field defaults: PASSED")

def run_all_tests():
    """Run all field mapping tests"""
    print("🧪 Running Hosting Plans Field Mapping Tests")
    print("=" * 50)
    
    try:
        test_old_database_schema_to_frontend()
        test_new_database_schema_to_frontend()
        test_frontend_to_database_mapping()
        test_mixed_schema_handling()
        test_empty_plan_handling()
        test_popular_field_defaults()
        
        print("\n" + "=" * 50)
        print("✅ All field mapping tests PASSED!")
        print("🎉 The bidirectional field mapping is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)