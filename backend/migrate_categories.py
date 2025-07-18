#!/usr/bin/env python3
"""
Migration Script for Blue Nebula Hosting - Category Management Fix

This script addresses the issues found in the category management system:
1. Ensures hosting categories exist in the database
2. Links existing plans to proper categories
3. Fixes any missing category_key fields in plans
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

async def run_migration():
    print("🔄 Running Category Management Migration...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Step 1: Ensure hosting categories exist
        await ensure_categories_exist(db)
        
        # Step 2: Fix existing plans to have proper category links
        await fix_plan_categories(db)
        
        # Step 3: Validate the migration
        await validate_migration(db)
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        client.close()

async def ensure_categories_exist(db):
    """Ensure all required hosting categories exist"""
    print("📂 Checking hosting categories...")
    
    # Count existing categories
    existing_count = await db.hosting_categories.count_documents({})
    print(f"📋 Found {existing_count} existing categories")
    
    if existing_count == 0:
        print("📦 Creating default hosting categories...")
        
        # Default hosting categories
        default_categories = [
            {
                "id": str(uuid.uuid4()),
                "key": "ssd_shared",
                "display_name": "SSD Shared Hosting",
                "description": "Fast SSD-powered shared hosting with premium features",
                "section_title": "SSD Shared Hosting",
                "section_description": "Fast SSD-powered shared hosting with premium features",
                "type": "shared",
                "sub_type": "ssd",
                "is_active": True,
                "display_order": 1,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "hdd_shared",
                "display_name": "HDD Shared Hosting",
                "description": "Affordable shared hosting with reliable HDD storage",
                "section_title": "HDD Shared Hosting",
                "section_description": "Affordable shared hosting with reliable HDD storage",
                "type": "shared",
                "sub_type": "hdd",
                "is_active": True,
                "display_order": 2,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "shared_byop",
                "display_name": "Build Your Own Plan",
                "description": "Customizable shared hosting with flexible resource allocation",
                "section_title": "Build Your Own Plan",
                "section_description": "Create a custom hosting plan tailored to your specific needs",
                "type": "shared",
                "sub_type": "byop",
                "is_active": True,
                "display_order": 3,
                "supports_custom_features": True,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "managed_wordpress",
                "display_name": "Dockerized Managed WordPress",
                "description": "Container-based WordPress hosting with auto-scaling",
                "section_title": "Dockerized Managed WordPress",
                "section_description": "Fully managed WordPress hosting in Docker containers",
                "type": "custom",
                "sub_type": "managed",
                "is_active": True,
                "display_order": 4,
                "supports_custom_features": False,
                "supports_containers": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "standard_vps",
                "display_name": "Standard VPS",
                "description": "Reliable VPS hosting with balanced performance and pricing",
                "section_title": "Standard VPS",
                "section_description": "Reliable VPS hosting with balanced performance and pricing",
                "type": "vps",
                "sub_type": "standard",
                "is_active": True,
                "display_order": 5,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "performance_vps",
                "display_name": "Performance VPS",
                "description": "High-performance VPS with premium hardware",
                "section_title": "Performance VPS",
                "section_description": "High-performance VPS with premium hardware and optimizations",
                "type": "vps",
                "sub_type": "performance",
                "is_active": True,
                "display_order": 6,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "standard_gameserver",
                "display_name": "Standard GameServer",
                "description": "Reliable game server hosting with Pterodactyl panel",
                "section_title": "Standard GameServer",
                "section_description": "Reliable game server hosting with Pterodactyl panel management",
                "type": "gameserver",
                "sub_type": "standard",
                "is_active": True,
                "display_order": 7,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "key": "performance_gameserver",
                "display_name": "Performance GameServer",
                "description": "High-performance game servers with enterprise hardware",
                "section_title": "Performance GameServer",
                "section_description": "High-performance game servers with enterprise hardware",
                "type": "gameserver",
                "sub_type": "performance",
                "is_active": True,
                "display_order": 8,
                "supports_custom_features": False,
                "supports_containers": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await db.hosting_categories.insert_many(default_categories)
        print(f"✅ Created {len(result.inserted_ids)} hosting categories")
    else:
        print("✅ Categories already exist, skipping creation")

async def fix_plan_categories(db):
    """Fix existing plans to have proper category links"""
    print("🔧 Fixing plan category links...")
    
    plans = await db.hosting_plans.find().to_list(1000)
    updated_count = 0
    
    for plan in plans:
        updates = {}
        
        # Map plan types to category keys
        plan_type = plan.get("plan_type") or plan.get("type", "")
        sub_type = plan.get("sub_type", "")
        
        # Determine the correct category_key based on type and sub_type
        category_key = None
        
        if plan_type == "shared" or "shared" in plan_type:
            if sub_type == "ssd" or "ssd" in plan_type:
                category_key = "ssd_shared"
            elif sub_type == "hdd" or "hdd" in plan_type:
                category_key = "hdd_shared"
            elif sub_type == "byop" or "byop" in plan_type:
                category_key = "shared_byop"
            else:
                category_key = "ssd_shared"  # Default
        elif plan_type == "vps":
            if sub_type == "performance":
                category_key = "performance_vps"
            else:
                category_key = "standard_vps"
        elif plan_type == "gameserver":
            if sub_type == "performance":
                category_key = "performance_gameserver"
            else:
                category_key = "standard_gameserver"
        elif "wordpress" in plan_type or plan.get("managed_wordpress"):
            category_key = "managed_wordpress"
        
        # Update plan if category_key is missing or wrong
        if category_key and plan.get("category_key") != category_key:
            updates["category_key"] = category_key
        
        # Ensure plan_type is set for backward compatibility
        if not plan.get("plan_type") and category_key:
            updates["plan_type"] = category_key
        
        # Apply updates if needed
        if updates:
            updates["updated_at"] = datetime.utcnow()
            await db.hosting_plans.update_one({"id": plan["id"]}, {"$set": updates})
            updated_count += 1
    
    print(f"✅ Updated {updated_count} hosting plans with category links")

async def validate_migration(db):
    """Validate that the migration was successful"""
    print("🔍 Validating migration...")
    
    # Check categories
    category_count = await db.hosting_categories.count_documents({"is_active": True})
    print(f"📂 Active categories: {category_count}")
    
    # Check plans with categories
    plans_with_categories = await db.hosting_plans.count_documents({"category_key": {"$exists": True, "$ne": None}})
    total_plans = await db.hosting_plans.count_documents({})
    print(f"📦 Plans with categories: {plans_with_categories}/{total_plans}")
    
    # List category distribution
    categories = await db.hosting_categories.find({"is_active": True}, {"key": 1, "display_name": 1}).to_list(100)
    for category in categories:
        plan_count = await db.hosting_plans.count_documents({"category_key": category["key"]})
        print(f"   📋 {category['display_name']} ({category['key']}): {plan_count} plans")
    
    print("✅ Migration validation complete")

if __name__ == "__main__":
    asyncio.run(run_migration())