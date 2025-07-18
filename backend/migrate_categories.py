#!/usr/bin/env python3
"""
Database migration script to initialize hosting categories.
This script populates the hosting_categories collection with predefined categories
and associates existing plans with their appropriate categories.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@bnhsite-mongodb:27017/blue_nebula_hosting?authSource=admin')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

# Predefined hosting categories to initialize
HOSTING_CATEGORIES = [
    {
        "id": str(uuid.uuid4()),
        "key": "ssd_shared",
        "display_name": "SSD Shared Hosting",
        "description": "High-performance shared hosting with SSD storage for faster website loading",
        "section_title": "SSD Shared Hosting Plans",
        "section_description": "Lightning-fast shared hosting with SSD storage and premium features",
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
        "description": "Affordable shared hosting with traditional HDD storage for budget-conscious users",
        "section_title": "HDD Shared Hosting Plans",
        "section_description": "Cost-effective shared hosting solutions with reliable HDD storage",
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
        "key": "standard_vps",
        "display_name": "Standard VPS",
        "description": "Reliable virtual private servers with dedicated resources and full control",
        "section_title": "Standard VPS Plans",
        "section_description": "Powerful virtual private servers with guaranteed resources and root access",
        "type": "vps",
        "sub_type": "standard",
        "is_active": True,
        "display_order": 3,
        "supports_custom_features": False,
        "supports_containers": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "key": "performance_vps",
        "display_name": "Performance VPS",
        "description": "High-performance VPS with enhanced CPU, memory, and SSD storage",
        "section_title": "Performance VPS Plans", 
        "section_description": "Premium VPS hosting with enhanced performance and SSD storage",
        "type": "vps",
        "sub_type": "performance",
        "is_active": True,
        "display_order": 4,
        "supports_custom_features": False,
        "supports_containers": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "key": "gameserver",
        "display_name": "Game Server Hosting",
        "description": "Specialized hosting for game servers with optimized performance and DDoS protection",
        "section_title": "Game Server Plans",
        "section_description": "High-performance game server hosting with instant setup and 24/7 support",
        "type": "gameserver",
        "sub_type": None,
        "is_active": True,
        "display_order": 5,
        "supports_custom_features": False,
        "supports_containers": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "key": "shared_byop",
        "display_name": "Build Your Own Plan",
        "description": "Customizable shared hosting plans where you can build your own configuration",
        "section_title": "Build Your Own Plan",
        "section_description": "Create a custom hosting plan tailored to your specific needs",
        "type": "custom",
        "sub_type": "byop",
        "is_active": True,
        "display_order": 6,
        "supports_custom_features": True,
        "supports_containers": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "key": "managed_wordpress",
        "display_name": "Dockerized WordPress",
        "description": "Managed WordPress hosting with Docker containers for enhanced performance and scalability",
        "section_title": "Dockerized WordPress Hosting",
        "section_description": "Premium WordPress hosting with Docker containers and managed services",
        "type": "custom",
        "sub_type": "managed",
        "is_active": True,
        "display_order": 7,
        "supports_custom_features": True,
        "supports_containers": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Category mapping for existing plan types
PLAN_TYPE_TO_CATEGORY_KEY = {
    "ssd_shared": "ssd_shared",
    "hdd_shared": "hdd_shared", 
    "standard_vps": "standard_vps",
    "performance_vps": "performance_vps",
    "gameserver": "gameserver",
    "shared_byop": "shared_byop",
    "managed_wordpress": "managed_wordpress"
}

async def migrate_categories():
    """Initialize hosting categories and associate existing plans"""
    client = None
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        print("Connected to MongoDB")
        print(f"Database: {DB_NAME}")
        
        # Check if categories already exist
        existing_count = await db.hosting_categories.count_documents({})
        print(f"Existing categories: {existing_count}")
        
        if existing_count > 0:
            print("Categories already exist. Checking for missing categories...")
            
            # Get existing category keys
            existing_categories = await db.hosting_categories.find({}, {"key": 1}).to_list(100)
            existing_keys = {cat["key"] for cat in existing_categories}
            
            # Insert only missing categories
            new_categories = [cat for cat in HOSTING_CATEGORIES if cat["key"] not in existing_keys]
            
            if new_categories:
                print(f"Inserting {len(new_categories)} new categories...")
                result = await db.hosting_categories.insert_many(new_categories)
                print(f"Inserted {len(result.inserted_ids)} new categories")
            else:
                print("All categories already exist")
        else:
            # Insert all categories
            print(f"Inserting {len(HOSTING_CATEGORIES)} categories...")
            result = await db.hosting_categories.insert_many(HOSTING_CATEGORIES)
            print(f"Inserted {len(result.inserted_ids)} categories")
        
        # Update existing plans to associate with categories
        print("\nUpdating existing plans with category associations...")
        
        plans = await db.hosting_plans.find({}).to_list(1000)
        updated_count = 0
        
        for plan in plans:
            plan_type = plan.get("plan_type")
            if plan_type and plan_type in PLAN_TYPE_TO_CATEGORY_KEY:
                category_key = PLAN_TYPE_TO_CATEGORY_KEY[plan_type]
                
                # Only update if category_key is not already set
                if not plan.get("category_key"):
                    result = await db.hosting_plans.update_one(
                        {"id": plan["id"]},
                        {"$set": {"category_key": category_key, "updated_at": datetime.utcnow()}}
                    )
                    if result.modified_count > 0:
                        updated_count += 1
                        print(f"  Updated plan {plan.get('plan_name', plan['id'])} -> {category_key}")
        
        print(f"\nUpdated {updated_count} plans with category associations")
        
        # Display summary
        print("\nMigration Summary:")
        categories = await db.hosting_categories.find({}).sort("display_order", 1).to_list(100)
        for category in categories:
            plan_count = await db.hosting_plans.count_documents({"category_key": category["key"]})
            print(f"  {category['display_name']} ({category['key']}): {plan_count} plans")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    print("Starting category migration...")
    asyncio.run(migrate_categories())