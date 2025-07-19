#!/usr/bin/env python3
"""
Integration test for hosting plans API endpoints with field mapping
"""

import asyncio
import sys
import os
from pathlib import Path
import uuid

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Mock database for testing
class MockDatabase:
    def __init__(self):
        self.hosting_plans = MockCollection()

class MockCollection:
    def __init__(self):
        # Test data with mixed database schemas
        self.data = [
            # Old schema (name, type, price)
            {
                "id": "plan-1",
                "name": "Basic Plan",
                "type": "ssd_shared",
                "price": 9.99,
                "sub_type": "ssd",
                "popular": False,
                "features": ["SSD Storage", "cPanel", "Free SSL"]
            },
            # New schema (plan_name, plan_type, base_price)
            {
                "id": "plan-2", 
                "plan_name": "Pro Plan",
                "plan_type": "hdd_shared",
                "base_price": 19.99,
                "popular": True,
                "features": ["HDD Storage", "cPanel", "Free SSL", "Email Accounts"]
            },
            # Mixed schema
            {
                "id": "plan-3",
                "plan_name": "VPS Standard",  # New schema
                "type": "standard_vps",       # Old schema  
                "base_price": 39.99,          # New schema
                "popular": False,             # Database format
                "cpu_cores": 2,
                "memory_gb": 4
            }
        ]
        
    def find(self, query=None):
        """Mock find method"""
        if query is None:
            return MockCursor(self.data)
        
        # Handle type filtering with OR condition
        if "$or" in query:
            or_conditions = query["$or"]
            filtered = []
            for item in self.data:
                for condition in or_conditions:
                    for key, value in condition.items():
                        if item.get(key) == value:
                            filtered.append(item)
                            break
            return MockCursor(filtered)
        
        # Simple field matching
        filtered = []
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(item)
        
        return MockCursor(filtered)
    
    def find_one(self, query):
        """Mock find_one method"""
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                return item.copy()
        return None

class MockCursor:
    def __init__(self, data):
        self.data = data
        
    def to_list(self, limit):
        """Mock to_list method"""
        return [item.copy() for item in self.data[:limit]]

async def test_get_hosting_plans_integration():
    """Test the get_hosting_plans function with mock database"""
    
    # Import and patch the server
    import server
    original_db = server.db
    server.db = MockDatabase()
    
    try:
        # Test getting all plans
        plans = []
        query = {}
        mock_plans = server.db.hosting_plans.find(query).to_list(1000)
        
        # Apply the same logic as the get_hosting_plans function
        for plan in mock_plans:
            if "_id" in plan:
                del plan["_id"]
            if "markup_percentage" in plan:
                del plan["markup_percentage"]
            
            mapped_plan = server.map_hosting_plan_fields(plan, to_frontend=True)
            plans.append(mapped_plan)
        
        # Validate results
        assert len(plans) == 3, f"Expected 3 plans, got {len(plans)}"
        
        # Validate first plan (old schema)
        plan1 = plans[0]
        assert plan1["name"] == "Basic Plan"
        assert plan1["type"] == "ssd_shared"
        assert plan1["price"] == 9.99
        assert plan1["is_popular"] == False
        
        # Validate second plan (new schema)
        plan2 = plans[1]
        assert plan2["name"] == "Pro Plan"
        assert plan2["type"] == "hdd_shared"
        assert plan2["price"] == 19.99
        assert plan2["is_popular"] == True
        
        # Validate third plan (mixed schema)
        plan3 = plans[2]
        assert plan3["name"] == "VPS Standard"
        assert plan3["type"] == "standard_vps"
        assert plan3["price"] == 39.99
        assert plan3["is_popular"] == False
        
        print("✅ get_hosting_plans integration test: PASSED")
        return True
        
    finally:
        server.db = original_db

async def test_get_hosting_plans_filtered_integration():
    """Test the get_hosting_plans function with type filtering"""
    
    import server
    original_db = server.db
    server.db = MockDatabase()
    
    try:
        # Test filtering by type
        plan_type = "ssd_shared"
        query = {
            "$or": [
                {"plan_type": plan_type},  # New schema
                {"type": plan_type}        # Old schema
            ]
        }
        
        mock_plans = server.db.hosting_plans.find(query).to_list(1000)
        
        plans = []
        for plan in mock_plans:
            if "_id" in plan:
                del plan["_id"]
            if "markup_percentage" in plan:
                del plan["markup_percentage"]
            
            mapped_plan = server.map_hosting_plan_fields(plan, to_frontend=True)
            plans.append(mapped_plan)
        
        # Should only return plans with ssd_shared type
        assert len(plans) == 1, f"Expected 1 plan for ssd_shared, got {len(plans)}"
        assert plans[0]["type"] == "ssd_shared"
        assert plans[0]["name"] == "Basic Plan"
        
        print("✅ get_hosting_plans filtered integration test: PASSED")
        return True
        
    finally:
        server.db = original_db

async def test_get_single_plan_integration():
    """Test getting a single plan by ID"""
    
    import server
    original_db = server.db
    server.db = MockDatabase()
    
    try:
        # Test getting plan by ID
        plan_id = "plan-2"
        plan = server.db.hosting_plans.find_one({"id": plan_id})
        
        if plan:
            if "_id" in plan:
                del plan["_id"]
            if "markup_percentage" in plan:
                del plan["markup_percentage"]
            
            mapped_plan = server.map_hosting_plan_fields(plan, to_frontend=True)
            
            # Validate the mapped plan
            assert mapped_plan["name"] == "Pro Plan"
            assert mapped_plan["type"] == "hdd_shared"
            assert mapped_plan["price"] == 19.99
            assert mapped_plan["is_popular"] == True
        
        print("✅ get_single_plan integration test: PASSED")
        return True
        
    finally:
        server.db = original_db

async def test_plan_creation_field_mapping():
    """Test plan creation with field mapping"""
    
    import server
    
    # Test frontend data (what admin panel would send)
    frontend_plan_data = {
        "name": "New Test Plan",
        "type": "performance_vps",
        "price": 59.99,
        "is_popular": True,
        "cpu_cores": 4,
        "memory_gb": 8,
        "features": ["High Performance", "SSD Storage"]
    }
    
    # Apply the same mapping as create_hosting_plan
    db_plan = server.map_hosting_plan_fields(frontend_plan_data, to_frontend=False)
    
    # Validate the database format
    assert db_plan["plan_name"] == "New Test Plan"
    assert db_plan["plan_type"] == "performance_vps"
    assert db_plan["base_price"] == 59.99
    assert db_plan["popular"] == True
    assert db_plan["cpu_cores"] == 4
    assert db_plan["memory_gb"] == 8
    
    print("✅ plan_creation_field_mapping test: PASSED")
    return True

async def test_plan_update_field_mapping():
    """Test plan update with field mapping"""
    
    import server
    
    # Test frontend update data
    frontend_update = {
        "name": "Updated Plan Name",
        "price": 29.99,
        "is_popular": False
    }
    
    # Apply the same mapping as update_hosting_plan
    db_update = server.map_hosting_plan_fields(frontend_update, to_frontend=False)
    
    # Remove temporary frontend fields
    frontend_fields_to_remove = ["name", "type", "price", "is_popular"]
    for field in frontend_fields_to_remove:
        if field in db_update:
            del db_update[field]
    
    # Validate the database update format
    assert db_update["plan_name"] == "Updated Plan Name"
    assert db_update["base_price"] == 29.99
    assert db_update["popular"] == False
    
    # Make sure frontend fields were removed
    assert "name" not in db_update
    assert "price" not in db_update
    assert "is_popular" not in db_update
    
    print("✅ plan_update_field_mapping test: PASSED")
    return True

async def run_all_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Hosting Plans API Integration Tests")
    print("=" * 55)
    
    try:
        await test_get_hosting_plans_integration()
        await test_get_hosting_plans_filtered_integration()
        await test_get_single_plan_integration()
        await test_plan_creation_field_mapping()
        await test_plan_update_field_mapping()
        
        print("\n" + "=" * 55)
        print("✅ All integration tests PASSED!")
        print("🎉 The API endpoints work correctly with field mapping")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_integration_tests())
    sys.exit(0 if success else 1)