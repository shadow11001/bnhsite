#!/usr/bin/env python3
"""
Dynamic Plan Management System Demo
This script demonstrates the key functionality of the new dynamic hosting plan management system.
"""

import asyncio
import json
from backend.server import (
    validate_resource_specs, 
    validate_plan_data, 
    CategoryCreate, 
    PlanCreate,
    HostingCategory,
    DynamicPlan
)

def demo_validation_system():
    """Demonstrate the validation system with various test cases"""
    
    print("🔍 DYNAMIC PLAN MANAGEMENT SYSTEM DEMO")
    print("=" * 50)
    
    # Example 1: WordPress Container Category
    print("\n📂 CATEGORY EXAMPLE: WordPress Containers")
    print("-" * 40)
    
    wp_category_data = {
        "name": "WordPress Containers",
        "type": "container", 
        "description": "Containerized WordPress hosting with auto-scaling",
        "features": [
            "Auto-scaling",
            "Managed WordPress", 
            "SSL Certificates",
            "CDN Integration",
            "Staging Environment"
        ],
        "resource_specs": {
            "required_fields": ["cpu_limit", "memory_limit", "storage", "traffic_limit"],
            "optional_fields": ["wordpress_sites", "staging_sites", "cdn_bandwidth"],
            "field_types": {
                "cpu_limit": "string",
                "memory_limit": "string",
                "storage": "string", 
                "traffic_limit": "string",
                "wordpress_sites": "integer",
                "staging_sites": "integer"
            }
        }
    }
    
    print("✅ Category Configuration:")
    print(f"   Type: {wp_category_data['type']}")
    print(f"   Required Fields: {wp_category_data['resource_specs']['required_fields']}")
    print(f"   Optional Fields: {wp_category_data['resource_specs']['optional_fields']}")
    
    # Example 2: Valid Plan Creation
    print("\n📋 PLAN EXAMPLE: WordPress Starter")
    print("-" * 40)
    
    valid_plan_resources = {
        "cpu_limit": "1 vCPU",
        "memory_limit": "2 GB RAM",
        "storage": "20 GB SSD",
        "traffic_limit": "100 GB/month",
        "wordpress_sites": 1,
        "staging_sites": 1
    }
    
    # Test resource validation
    is_valid = validate_resource_specs(valid_plan_resources, wp_category_data["resource_specs"])
    print(f"✅ Resource Validation Result: {is_valid}")
    
    # Example plan data for validation
    plan_data = {
        "category": "wp_container_category_id",
        "name": "WordPress Starter",
        "description": "Perfect for small WordPress sites",
        "price": 15.99,
        "resources": valid_plan_resources,
        "features": [
            "1 WordPress Site",
            "Free SSL Certificate", 
            "Daily Backups",
            "24/7 Support"
        ],
        "billing_cycle": "monthly"
    }
    
    # Test plan validation with category rules
    category_with_rules = {
        **wp_category_data,
        "validation_rules": {
            "price_min": 5.0,
            "price_max": 200.0,
            "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
        }
    }
    
    validation_errors = validate_plan_data(plan_data, category_with_rules)
    print(f"✅ Plan Validation Result: {len(validation_errors)} errors")
    if validation_errors:
        for error in validation_errors:
            print(f"   ❌ {error}")
    
    print("\n📊 PLAN DETAILS:")
    print(f"   Name: {plan_data['name']}")
    print(f"   Price: ${plan_data['price']}/month")
    print(f"   Resources: {json.dumps(plan_data['resources'], indent=6)}")
    
    # Example 3: Invalid Plan Testing
    print("\n❌ VALIDATION ERROR EXAMPLES")
    print("-" * 40)
    
    # Test 1: Missing required field
    invalid_resources_missing = {
        "cpu_limit": "1 vCPU",
        "memory_limit": "2 GB RAM"
        # Missing required fields: storage, traffic_limit
    }
    
    is_valid = validate_resource_specs(invalid_resources_missing, wp_category_data["resource_specs"])
    print(f"Missing required fields: {is_valid}")
    
    # Test 2: Invalid field
    invalid_resources_extra = {
        "cpu_limit": "1 vCPU",
        "memory_limit": "2 GB RAM", 
        "storage": "20 GB SSD",
        "traffic_limit": "100 GB/month",
        "invalid_field": "should not be here"  # Invalid field
    }
    
    is_valid = validate_resource_specs(invalid_resources_extra, wp_category_data["resource_specs"])
    print(f"Invalid extra field: {is_valid}")
    
    # Test 3: Price too low
    invalid_plan_price = {
        **plan_data,
        "price": 2.0  # Below minimum of 5.0
    }
    
    validation_errors = validate_plan_data(invalid_plan_price, category_with_rules)
    print(f"Price too low: {len(validation_errors)} errors")
    for error in validation_errors:
        print(f"   ❌ {error}")
    
    # Example 4: Different Category Types
    print("\n🔧 DIFFERENT CATEGORY TYPES")
    print("-" * 40)
    
    # VPS Category
    vps_category = {
        "name": "Performance VPS",
        "type": "vps",
        "resource_specs": {
            "required_fields": ["cpu", "ram", "disk_space", "bandwidth"],
            "optional_fields": ["ip_addresses", "os_choices", "backup_frequency"]
        },
        "validation_rules": {
            "price_min": 5.0,
            "price_max": 500.0,
            "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
        }
    }
    
    vps_plan_resources = {
        "cpu": "4 vCPU",
        "ram": "8 GB RAM",
        "disk_space": "160 GB NVMe SSD", 
        "bandwidth": "Unlimited",
        "ip_addresses": "1 Dedicated IP"
    }
    
    is_valid = validate_resource_specs(vps_plan_resources, vps_category["resource_specs"])
    print(f"✅ VPS Plan Resources Valid: {is_valid}")
    
    # GameServer Category
    gameserver_category = {
        "name": "Performance GameServer",
        "type": "gameserver",
        "resource_specs": {
            "required_fields": ["cpu", "ram", "disk_space", "max_players"],
            "optional_fields": ["bandwidth", "supported_games", "control_panel"]
        },
        "validation_rules": {
            "price_min": 5.0,
            "price_max": 400.0,
            "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
        }
    }
    
    gameserver_plan_resources = {
        "cpu": "6 vCPU",
        "ram": "12 GB RAM",
        "disk_space": "120 GB NVMe SSD",
        "max_players": "64 Players",
        "control_panel": "Pterodactyl"
    }
    
    is_valid = validate_resource_specs(gameserver_plan_resources, gameserver_category["resource_specs"])
    print(f"✅ GameServer Plan Resources Valid: {is_valid}")
    
    print("\n🎯 SYSTEM FEATURES DEMONSTRATED:")
    print("-" * 40)
    print("✅ Dynamic category creation with custom resource specifications")
    print("✅ Flexible plan creation within categories")
    print("✅ Category-specific validation rules") 
    print("✅ Resource specification validation")
    print("✅ Price and billing cycle validation")
    print("✅ Support for multiple hosting types (container, vps, gameserver)")
    print("✅ Comprehensive error handling and validation feedback")
    
    print("\n🚀 Ready for production use!")
    print("   • Use the migration script to set up database collections")
    print("   • Start creating categories via POST /api/admin/categories") 
    print("   • Create plans within categories via POST /api/admin/plans")
    print("   • Plans automatically appear in public API at /api/hosting-plans")

if __name__ == "__main__":
    demo_validation_system()