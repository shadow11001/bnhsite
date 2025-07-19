#!/usr/bin/env python3
"""
Simple Field Mapping Test
Tests the field mapping utility function to ensure it correctly maps fields
and preserves data values without external dependencies.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from field_mapping_utils import map_hosting_plan_fields

def test_field_mapping():
    """Test the field mapping function"""
    print("🧪 Testing Field Mapping Utility")
    print("=" * 40)
    
    test_documents = [
        # Old schema document
        {
            "id": "test_1",
            "plan_name": "Basic Shared",
            "plan_type": "shared",
            "base_price": 9.99,
            "popular": True,
            "cpu_cores": 1,
            "memory_gb": 2,
            "disk_gb": 10,
            "features": ["SSD Storage", "Email Support"]
        },
        # New schema document
        {
            "id": "test_2", 
            "name": "VPS Standard",
            "type": "vps",
            "price": 29.99,
            "is_popular": False,
            "cpu_cores": 2,
            "memory_gb": 4,
            "disk_gb": 50,
            "features": ["Root Access", "SSD Storage"]
        },
        # Mixed schema document
        {
            "id": "test_3",
            "plan_name": "Game Server Pro",  # old field
            "type": "gameserver",           # new field
            "base_price": 49.99,           # old field
            "is_popular": True,            # new field
            "supported_games": ["Minecraft", "CS:GO"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, doc in enumerate(test_documents):
        print(f"\n📋 Document {i+1}: {doc.get('name', doc.get('plan_name', 'unnamed'))}")
        print(f"   Original: {doc}")
        
        # Test to_frontend mapping
        frontend_mapped = map_hosting_plan_fields(doc, to_frontend=True)
        print(f"   Frontend: {frontend_mapped}")
        
        # Test to_database mapping
        database_mapped = map_hosting_plan_fields(frontend_mapped, to_frontend=False)
        print(f"   Database: {database_mapped}")
        
        # Check essential field mappings for frontend
        checks = [
            ('name' in frontend_mapped, f"Frontend should have 'name' field"),
            ('type' in frontend_mapped, f"Frontend should have 'type' field"),
            ('price' in frontend_mapped, f"Frontend should have 'price' field"),
            ('plan_name' in database_mapped, f"Database should have 'plan_name' field"),
            ('plan_type' in database_mapped, f"Database should have 'plan_type' field"),
            ('base_price' in database_mapped, f"Database should have 'base_price' field"),
        ]
        
        for check_passed, message in checks:
            if check_passed:
                print(f"   ✅ {message}")
                passed += 1
            else:
                print(f"   ❌ {message}")
                failed += 1
        
        # Test data preservation
        original_name = doc.get('name', doc.get('plan_name'))
        frontend_name = frontend_mapped.get('name')
        database_name = database_mapped.get('plan_name')
        
        if original_name == frontend_name == database_name:
            print(f"   ✅ Name preserved through mapping: {original_name}")
            passed += 1
        else:
            print(f"   ❌ Name not preserved: {original_name} → {frontend_name} → {database_name}")
            failed += 1
        
        original_price = doc.get('price', doc.get('base_price'))
        frontend_price = frontend_mapped.get('price')
        database_price = database_mapped.get('base_price')
        
        if original_price == frontend_price == database_price:
            print(f"   ✅ Price preserved through mapping: {original_price}")
            passed += 1
        else:
            print(f"   ❌ Price not preserved: {original_price} → {frontend_price} → {database_price}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests PASSED! Field mapping is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED! Field mapping needs review.")
        return False

def test_edge_cases():
    """Test edge cases and special scenarios"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 40)
    
    edge_cases = [
        # Empty document
        {},
        # None document
        None,
        # Document with only old fields
        {"plan_name": "Test", "plan_type": "shared", "base_price": 10.0, "popular": False},
        # Document with only new fields
        {"name": "Test", "type": "shared", "price": 10.0, "is_popular": False},
        # Document with conflicting fields (both old and new)
        {"name": "New Name", "plan_name": "Old Name", "type": "new_type", "plan_type": "old_type"},
    ]
    
    passed = 0
    failed = 0
    
    for i, doc in enumerate(edge_cases):
        print(f"\n📋 Edge Case {i+1}: {doc}")
        
        try:
            frontend_mapped = map_hosting_plan_fields(doc, to_frontend=True)
            database_mapped = map_hosting_plan_fields(doc, to_frontend=False)
            
            print(f"   ✅ Mapping successful")
            print(f"   Frontend: {frontend_mapped}")
            print(f"   Database: {database_mapped}")
            passed += 1
        except Exception as e:
            print(f"   ❌ Mapping failed with error: {e}")
            failed += 1
    
    print(f"\n📊 Edge Case Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all tests"""
    test1_passed = test_field_mapping()
    test2_passed = test_edge_cases()
    
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS:")
    print(f"✅ Field mapping tests: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Edge case tests: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests PASSED! Field mapping utility is ready for use.")
        return 0
    else:
        print("\n❌ Some tests FAILED! Please review the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)