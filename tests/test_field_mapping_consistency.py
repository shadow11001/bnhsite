#!/usr/bin/env python3
"""
Test Field Mapping Consistency
Ensures that the database reorganization field mapping is consistent with server.py
and only changes field names, not data values.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from field_mapping_utils import map_hosting_plan_fields
from schema_migration import SchemaMigration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFieldMappingConsistency:
    """Test field mapping consistency between server.py and schema_migration.py"""
    
    def __init__(self):
        self.test_documents = [
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
    
    def test_server_mapping_consistency(self):
        """Test that server.py mapping is bidirectional and consistent"""
        print("🔍 Testing server.py field mapping consistency...")
        
        passed = 0
        failed = 0
        
        for i, doc in enumerate(self.test_documents):
            print(f"\n  Document {i+1}: {doc.get('name', doc.get('plan_name', 'unnamed'))}")
            
            # Test to_frontend mapping
            frontend_mapped = map_hosting_plan_fields(doc, to_frontend=True)
            
            # Test to_database mapping (reverse)
            database_mapped = map_hosting_plan_fields(frontend_mapped, to_frontend=False)
            
            # Check essential field mappings
            checks = [
                # Frontend should have these fields
                ('name' in frontend_mapped, "Frontend mapping should have 'name' field"),
                ('type' in frontend_mapped, "Frontend mapping should have 'type' field"),
                ('price' in frontend_mapped, "Frontend mapping should have 'price' field"),
                
                # Database should have these fields
                ('plan_name' in database_mapped, "Database mapping should have 'plan_name' field"),
                ('plan_type' in database_mapped, "Database mapping should have 'plan_type' field"),
                ('base_price' in database_mapped, "Database mapping should have 'base_price' field"),
            ]
            
            for check_passed, message in checks:
                if check_passed:
                    print(f"    ✅ {message}")
                    passed += 1
                else:
                    print(f"    ❌ {message}")
                    failed += 1
            
            # Test that data values are preserved
            if 'name' in frontend_mapped or 'plan_name' in doc:
                original_name = doc.get('name', doc.get('plan_name'))
                mapped_name = frontend_mapped.get('name')
                if original_name == mapped_name:
                    print(f"    ✅ Name value preserved: {original_name}")
                    passed += 1
                else:
                    print(f"    ❌ Name value changed: {original_name} → {mapped_name}")
                    failed += 1
            
            if 'price' in frontend_mapped or 'base_price' in doc:
                original_price = doc.get('price', doc.get('base_price'))
                mapped_price = frontend_mapped.get('price')
                if original_price == mapped_price:
                    print(f"    ✅ Price value preserved: {original_price}")
                    passed += 1
                else:
                    print(f"    ❌ Price value changed: {original_price} → {mapped_price}")
                    failed += 1
        
        print(f"\n📊 Server mapping tests: {passed} passed, {failed} failed")
        return failed == 0
    
    async def test_schema_migration_consistency(self):
        """Test that schema migration uses consistent field mapping and preserves data"""
        print("🔍 Testing schema migration field mapping consistency...")
        
        # Create migration instance (without connecting to database)
        migration = SchemaMigration("mongodb://dummy", "test_db")
        
        passed = 0
        failed = 0
        
        for i, doc in enumerate(self.test_documents):
            print(f"\n  Document {i+1}: {doc.get('name', doc.get('plan_name', 'unnamed'))}")
            
            # Test migration with preserve_data_only=True
            migrated_doc = migration.migrate_hosting_plan_document(doc, preserve_data_only=True)
            
            # Check that essential fields are properly mapped
            checks = [
                ('name' in migrated_doc, "Migrated doc should have 'name' field"),
                ('type' in migrated_doc, "Migrated doc should have 'type' field"),
                ('price' in migrated_doc, "Migrated doc should have 'price' field"),
            ]
            
            for check_passed, message in checks:
                if check_passed:
                    print(f"    ✅ {message}")
                    passed += 1
                else:
                    print(f"    ❌ {message}")
                    failed += 1
            
            # Test that data values are preserved
            original_name = doc.get('name', doc.get('plan_name'))
            migrated_name = migrated_doc.get('name')
            if original_name == migrated_name:
                print(f"    ✅ Name value preserved: {original_name}")
                passed += 1
            else:
                print(f"    ❌ Name value changed: {original_name} → {migrated_name}")
                failed += 1
            
            original_price = doc.get('price', doc.get('base_price'))
            migrated_price = migrated_doc.get('price')
            if original_price == migrated_price:
                print(f"    ✅ Price value preserved: {original_price}")
                passed += 1
            else:
                print(f"    ❌ Price value changed: {original_price} → {migrated_price}")
                failed += 1
            
            # Test that original fields are preserved
            for field, value in doc.items():
                if field in migrated_doc and field != '_id':
                    if migrated_doc[field] == value:
                        print(f"    ✅ Field '{field}' preserved")
                        passed += 1
                    else:
                        print(f"    ❌ Field '{field}' changed: {value} → {migrated_doc[field]}")
                        failed += 1
        
        print(f"\n📊 Schema migration tests: {passed} passed, {failed} failed")
        return failed == 0
    
    async def test_bidirectional_mapping(self):
        """Test that mapping is truly bidirectional"""
        print("🔍 Testing bidirectional mapping...")
        
        passed = 0
        failed = 0
        
        for i, doc in enumerate(self.test_documents):
            print(f"\n  Document {i+1}: {doc.get('name', doc.get('plan_name', 'unnamed'))}")
            
            # Test round-trip: original → frontend → database → frontend
            step1_frontend = map_hosting_plan_fields(doc, to_frontend=True)
            step2_database = map_hosting_plan_fields(step1_frontend, to_frontend=False)
            step3_frontend = map_hosting_plan_fields(step2_database, to_frontend=True)
            
            # Compare step1 and step3 (should be identical)
            essential_fields = ['name', 'type', 'price', 'is_popular']
            
            for field in essential_fields:
                if field in step1_frontend and field in step3_frontend:
                    if step1_frontend[field] == step3_frontend[field]:
                        print(f"    ✅ Round-trip preserved '{field}': {step1_frontend[field]}")
                        passed += 1
                    else:
                        print(f"    ❌ Round-trip changed '{field}': {step1_frontend[field]} → {step3_frontend[field]}")
                        failed += 1
        
        print(f"\n📊 Bidirectional mapping tests: {passed} passed, {failed} failed")
        return failed == 0

async def main():
    """Run all field mapping consistency tests"""
    print("🧪 Field Mapping Consistency Tests")
    print("=" * 50)
    
    tester = TestFieldMappingConsistency()
    
    # Run tests
    test1_passed = tester.test_server_mapping_consistency()
    test2_passed = await tester.test_schema_migration_consistency()
    test3_passed = await tester.test_bidirectional_mapping()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"✅ Server mapping consistency: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Schema migration consistency: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"✅ Bidirectional mapping: {'PASSED' if test3_passed else 'FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests PASSED! Field mapping is consistent and data-preserving.")
        return 0
    else:
        print("\n❌ Some tests FAILED! Please review the field mapping implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)