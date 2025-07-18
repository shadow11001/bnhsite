import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from server import app, db
import uuid
from datetime import datetime

# Test configuration
TEST_DB_NAME = "test_blue_nebula_hosting"
TEST_CATEGORY_ID = str(uuid.uuid4())
TEST_PLAN_ID = str(uuid.uuid4())

@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_db():
    """Mock the database for testing"""
    return AsyncMock()

@pytest.fixture
def sample_category():
    """Sample category for testing"""
    return {
        "id": TEST_CATEGORY_ID,
        "name": "Test VPS",
        "type": "vps",
        "description": "Test VPS category",
        "features": ["Test Feature 1", "Test Feature 2"],
        "resource_specs": {
            "required_fields": ["cpu", "ram", "disk_space"],
            "optional_fields": ["bandwidth"],
            "field_types": {
                "cpu": "string",
                "ram": "string", 
                "disk_space": "string",
                "bandwidth": "string"
            }
        },
        "validation_rules": {
            "price_min": 1.0,
            "price_max": 100.0,
            "allowed_billing_cycles": ["monthly", "yearly"]
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def sample_plan():
    """Sample plan for testing"""
    return {
        "id": TEST_PLAN_ID,
        "category_id": TEST_CATEGORY_ID,
        "category_type": "vps",
        "name": "Test VPS Plan",
        "description": "A test VPS plan",
        "price": 25.0,
        "resources": {
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited"
        },
        "features": ["Full Root Access", "DDoS Protection"],
        "billing_cycle": "monthly",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test_token"}

class TestCategoryManagement:
    """Test cases for category management endpoints"""
    
    @pytest.mark.asyncio
    @patch('server.get_current_user')
    @patch('server.db')
    async def test_get_categories(self, mock_db, mock_auth, async_client, sample_category, auth_headers):
        """Test getting all categories"""
        mock_auth.return_value = "test_user"
        mock_db.hosting_categories.find.return_value.to_list.return_value = [sample_category]
        
        response = await async_client.get("/api/admin/categories", headers=auth_headers)
        
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 1
        assert categories[0]["name"] == "Test VPS"

    @pytest.mark.asyncio
    @patch('server.get_current_user')
    @patch('server.check_duplicate_category')
    @patch('server.db')
    async def test_create_category_success(self, mock_db, mock_duplicate, mock_auth, async_client, auth_headers):
        """Test successfully creating a category"""
        mock_auth.return_value = "test_user"
        mock_duplicate.return_value = False
        mock_db.hosting_categories.insert_one.return_value = AsyncMock(inserted_id="test_id")
        
        category_data = {
            "name": "Test Category",
            "type": "vps",
            "description": "Test description",
            "features": ["Feature 1"],
            "resource_specs": {
                "required_fields": ["cpu", "ram"],
                "optional_fields": ["bandwidth"]
            }
        }
        
        response = await async_client.post("/api/admin/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Category created successfully"

    @pytest.mark.asyncio
    @patch('server.get_current_user')
    @patch('server.check_duplicate_category')
    async def test_create_category_duplicate_name(self, mock_duplicate, mock_auth, async_client, auth_headers):
        """Test creating a category with duplicate name"""
        mock_auth.return_value = "test_user"
        mock_duplicate.return_value = True
        
        category_data = {
            "name": "Duplicate Category",
            "type": "vps",
            "description": "Test description",
            "features": ["Feature 1"],
            "resource_specs": {"required_fields": ["cpu"]}
        }
        
        response = await async_client.post("/api/admin/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

class TestPlanManagement:
    """Test cases for plan management endpoints"""
    
    @pytest.mark.asyncio
    @patch('server.get_current_user')
    @patch('server.db')
    async def test_get_admin_plans(self, mock_db, mock_auth, async_client, sample_plan, auth_headers):
        """Test getting all plans for admin"""
        mock_auth.return_value = "test_user"
        mock_db.hosting_plans.find.return_value.to_list.return_value = []
        mock_db.dynamic_plans.find.return_value.to_list.return_value = [sample_plan]
        
        response = await async_client.get("/api/admin/plans", headers=auth_headers)
        
        assert response.status_code == 200
        plans = response.json()
        assert len(plans) == 1
        assert plans[0]["name"] == "Test VPS Plan"

    @pytest.mark.asyncio
    @patch('server.get_current_user')
    @patch('server.db')
    @patch('server.validate_plan_data')
    @patch('server.check_duplicate_plan')
    async def test_create_plan_success(self, mock_duplicate, mock_validate, mock_db, mock_auth, async_client, sample_category, auth_headers):
        """Test successfully creating a plan"""
        mock_auth.return_value = "test_user"
        mock_db.hosting_categories.find_one.return_value = sample_category
        mock_validate.return_value = []  # No validation errors
        mock_duplicate.return_value = False
        mock_db.dynamic_plans.insert_one.return_value = AsyncMock(inserted_id="test_id")
        
        plan_data = {
            "category": TEST_CATEGORY_ID,
            "name": "Test Plan",
            "description": "Test plan description",
            "price": 25.0,
            "resources": {
                "cpu": "2 vCPU",
                "ram": "4 GB RAM",
                "disk_space": "50 GB SSD"
            },
            "features": ["Feature 1"],
            "billing_cycle": "monthly"
        }
        
        response = await async_client.post("/api/admin/plans", json=plan_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Plan created successfully"

    @patch('server.get_current_user')
    @patch('server.db')
    async def test_create_plan_invalid_category(self, mock_db, mock_auth, async_client, auth_headers):
        """Test creating a plan with invalid category"""
        mock_auth.return_value = "test_user"
        mock_db.hosting_categories.find_one.return_value = None
        
        plan_data = {
            "category": "invalid_category_id",
            "name": "Test Plan",
            "description": "Test description",
            "price": 25.0,
            "resources": {"cpu": "2 vCPU"},
            "features": ["Feature 1"],
            "billing_cycle": "monthly"
        }
        
        response = await async_client.post("/api/admin/plans", json=plan_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Category not found" in response.json()["detail"]

    @patch('server.get_current_user')
    @patch('server.db')
    async def test_delete_plan_success(self, mock_db, mock_auth, async_client, auth_headers):
        """Test successfully deleting a plan"""
        mock_auth.return_value = "test_user"
        mock_db.dynamic_plans.delete_one.return_value = AsyncMock(deleted_count=1)
        
        response = await async_client.delete(f"/api/admin/plans/{TEST_PLAN_ID}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Plan deleted successfully"

    @patch('server.get_current_user')
    @patch('server.db')
    async def test_delete_plan_not_found(self, mock_db, mock_auth, async_client, auth_headers):
        """Test deleting a non-existent plan"""
        mock_auth.return_value = "test_user"
        mock_db.dynamic_plans.delete_one.return_value = AsyncMock(deleted_count=0)
        
        response = await async_client.delete(f"/api/admin/plans/{TEST_PLAN_ID}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Plan not found" in response.json()["detail"]

class TestValidation:
    """Test cases for validation functions"""
    
    def test_validate_resource_specs_success(self):
        """Test successful resource validation"""
        from server import validate_resource_specs
        
        resources = {
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "50 GB SSD"
        }
        
        category_specs = {
            "required_fields": ["cpu", "ram", "disk_space"],
            "optional_fields": ["bandwidth"]
        }
        
        assert validate_resource_specs(resources, category_specs) == True

    def test_validate_resource_specs_missing_required(self):
        """Test validation with missing required field"""
        from server import validate_resource_specs
        
        resources = {
            "cpu": "2 vCPU",
            "ram": "4 GB RAM"
            # Missing required disk_space
        }
        
        category_specs = {
            "required_fields": ["cpu", "ram", "disk_space"],
            "optional_fields": ["bandwidth"]
        }
        
        assert validate_resource_specs(resources, category_specs) == False

    def test_validate_resource_specs_invalid_field(self):
        """Test validation with invalid field"""
        from server import validate_resource_specs
        
        resources = {
            "cpu": "2 vCPU",
            "ram": "4 GB RAM", 
            "disk_space": "50 GB SSD",
            "invalid_field": "value"  # Not allowed
        }
        
        category_specs = {
            "required_fields": ["cpu", "ram", "disk_space"],
            "optional_fields": ["bandwidth"]
        }
        
        assert validate_resource_specs(resources, category_specs) == False

    def test_validate_plan_data_success(self):
        """Test successful plan data validation"""
        from server import validate_plan_data
        
        plan_data = {
            "price": 25.0,
            "billing_cycle": "monthly",
            "resources": {
                "cpu": "2 vCPU",
                "ram": "4 GB RAM",
                "disk_space": "50 GB SSD"
            }
        }
        
        category = {
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space"],
                "optional_fields": ["bandwidth"]
            },
            "validation_rules": {
                "price_min": 1.0,
                "price_max": 100.0,
                "allowed_billing_cycles": ["monthly", "yearly"]
            }
        }
        
        errors = validate_plan_data(plan_data, category)
        assert len(errors) == 0

    def test_validate_plan_data_price_too_low(self):
        """Test validation with price too low"""
        from server import validate_plan_data
        
        plan_data = {
            "price": 0.5,  # Below minimum
            "billing_cycle": "monthly",
            "resources": {
                "cpu": "2 vCPU",
                "ram": "4 GB RAM",
                "disk_space": "50 GB SSD"
            }
        }
        
        category = {
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space"],
                "optional_fields": []
            },
            "validation_rules": {
                "price_min": 1.0,
                "price_max": 100.0,
                "allowed_billing_cycles": ["monthly", "yearly"]
            }
        }
        
        errors = validate_plan_data(plan_data, category)
        assert len(errors) > 0
        assert "Price must be at least" in errors[0]

class TestPublicPlanEndpoints:
    """Test cases for public plan endpoints"""
    
    @patch('server.db')
    async def test_get_hosting_plans_mixed_sources(self, mock_db, async_client, sample_plan):
        """Test getting hosting plans from both legacy and dynamic sources"""
        legacy_plan = {
            "id": "legacy_1",
            "plan_type": "shared",
            "plan_name": "Legacy Plan",
            "base_price": 10.0,
            "popular": False
        }
        
        mock_db.hosting_plans.find.return_value.to_list.return_value = [legacy_plan]
        mock_db.dynamic_plans.find.return_value.to_list.return_value = [sample_plan]
        
        response = await async_client.get("/api/hosting-plans")
        
        assert response.status_code == 200
        plans = response.json()
        assert len(plans) == 2
        
        # Check legacy plan mapping
        legacy_result = next(p for p in plans if p.get("plan_source") == "legacy")
        assert legacy_result["name"] == "Legacy Plan"
        assert legacy_result["type"] == "shared"
        
        # Check dynamic plan mapping
        dynamic_result = next(p for p in plans if p.get("plan_source") == "dynamic")
        assert dynamic_result["name"] == "Test VPS Plan"
        assert dynamic_result["type"] == "vps"

    @patch('server.db')
    async def test_get_hosting_plans_category_filter(self, mock_db, async_client, sample_plan):
        """Test filtering plans by category"""
        mock_db.hosting_plans.find.return_value.to_list.return_value = []
        mock_db.dynamic_plans.find.return_value.to_list.return_value = [sample_plan]
        
        response = await async_client.get(f"/api/hosting-plans?category={TEST_CATEGORY_ID}")
        
        assert response.status_code == 200
        plans = response.json()
        assert len(plans) == 1
        assert plans[0]["category_id"] == TEST_CATEGORY_ID

if __name__ == "__main__":
    pytest.main([__file__, "-v"])