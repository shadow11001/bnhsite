#!/usr/bin/env python3
"""
Blue Nebula Hosting - Dynamic Plan Management Migration Script
This script migrates the database to support dynamic plan management while preserving existing data.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

async def migrate_to_dynamic_plans():
    """
    Migrate database to support dynamic plan management.
    This preserves all existing data while adding new collections and schemas.
    """
    print("🔄 Starting migration to dynamic plan management...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Initialize default categories based on existing plan types
        await create_default_categories(db)
        
        # Create indexes for better performance
        await create_indexes(db)
        
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e
    finally:
        client.close()

async def create_default_categories(db):
    """Create default hosting categories based on existing plan structure"""
    print("📂 Creating default hosting categories...")
    
    # Check if categories already exist
    existing_count = await db.hosting_categories.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing categories. Skipping category creation.")
        return
    
    default_categories = [
        {
            "id": str(uuid.uuid4()),
            "name": "SSD Shared Hosting",
            "type": "shared",
            "description": "High-performance shared hosting with SSD storage for faster website loading",
            "features": [
                "SSD Storage",
                "cPanel Control Panel", 
                "Free SSL Certificate",
                "Daily Backups",
                "99.9% Uptime Guarantee"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "bandwidth"],
                "optional_fields": ["websites", "subdomains", "databases", "email_accounts", "ssl_certificate"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string", 
                    "disk_space": "string",
                    "bandwidth": "string",
                    "websites": "integer_or_string",
                    "subdomains": "string",
                    "databases": "integer",
                    "email_accounts": "string"
                }
            },
            "validation_rules": {
                "price_min": 0.5,
                "price_max": 50.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Free SSL Certificate", "Daily Backups", "24/7 Support"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "HDD Shared Hosting", 
            "type": "shared",
            "description": "Cost-effective shared hosting with traditional HDD storage",
            "features": [
                "HDD Storage",
                "cPanel Control Panel",
                "Free SSL Certificate", 
                "Daily Backups",
                "99.9% Uptime Guarantee"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "bandwidth"],
                "optional_fields": ["websites", "subdomains", "databases", "email_accounts", "ssl_certificate"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string",
                    "disk_space": "string", 
                    "bandwidth": "string",
                    "websites": "integer_or_string",
                    "subdomains": "string",
                    "databases": "integer",
                    "email_accounts": "string"
                }
            },
            "validation_rules": {
                "price_min": 0.5,
                "price_max": 150.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Free SSL Certificate", "Daily Backups", "24/7 Support"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Standard VPS",
            "type": "vps", 
            "description": "Virtual private servers with dedicated resources for better performance",
            "features": [
                "Full Root Access",
                "Choice of Operating System",
                "Dedicated IP Address",
                "SSD Storage",
                "DDoS Protection"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "bandwidth"],
                "optional_fields": ["ip_addresses", "os_choices", "backup_frequency", "support_level"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string",
                    "disk_space": "string",
                    "bandwidth": "string", 
                    "ip_addresses": "string",
                    "os_choices": "string"
                }
            },
            "validation_rules": {
                "price_min": 1.0,
                "price_max": 200.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Full Root Access", "DDoS Protection", "24/7 Support"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance VPS",
            "type": "vps",
            "description": "High-performance VPS with NVMe SSD storage and premium support",
            "features": [
                "Full Root Access",
                "NVMe SSD Storage",
                "Premium Support", 
                "DDoS Protection",
                "Dedicated IP Address"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "bandwidth"],
                "optional_fields": ["ip_addresses", "os_choices", "backup_frequency", "support_level"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string",
                    "disk_space": "string",
                    "bandwidth": "string",
                    "ip_addresses": "string", 
                    "os_choices": "string"
                }
            },
            "validation_rules": {
                "price_min": 5.0,
                "price_max": 500.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDoS Protection"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Standard GameServer",
            "type": "gameserver",
            "description": "Game servers for popular games with instant setup and DDoS protection",
            "features": [
                "Game Panel",
                "Instant Setup",
                "DDoS Protection",
                "24/7 Support",
                "Automatic Backups"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "max_players"],
                "optional_fields": ["bandwidth", "supported_games", "control_panel", "backup_frequency"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string",
                    "disk_space": "string",
                    "max_players": "string",
                    "bandwidth": "string",
                    "supported_games": "array"
                }
            },
            "validation_rules": {
                "price_min": 2.0,
                "price_max": 150.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance GameServer",
            "type": "gameserver",
            "description": "High-performance game servers with NVMe storage and priority support",
            "features": [
                "Premium Game Panel",
                "NVMe Storage",
                "Priority Support",
                "DDoS Protection", 
                "Automatic Backups"
            ],
            "resource_specs": {
                "required_fields": ["cpu", "ram", "disk_space", "max_players"],
                "optional_fields": ["bandwidth", "supported_games", "control_panel", "backup_frequency"],
                "field_types": {
                    "cpu": "string",
                    "ram": "string",
                    "disk_space": "string",
                    "max_players": "string",
                    "bandwidth": "string",
                    "supported_games": "array"
                }
            },
            "validation_rules": {
                "price_min": 5.0,
                "price_max": 400.0,
                "allowed_billing_cycles": ["monthly", "quarterly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WordPress Containers",
            "type": "container",
            "description": "Containerized WordPress hosting with automatic scaling and management", 
            "features": [
                "Auto-scaling",
                "Managed WordPress",
                "SSL Certificates",
                "CDN Integration",
                "Staging Environment"
            ],
            "resource_specs": {
                "required_fields": ["cpu_limit", "memory_limit", "storage", "traffic_limit"],
                "optional_fields": ["wordpress_sites", "staging_sites", "cdn_bandwidth", "ssl_certificates"],
                "field_types": {
                    "cpu_limit": "string",
                    "memory_limit": "string", 
                    "storage": "string",
                    "traffic_limit": "string",
                    "wordpress_sites": "integer",
                    "staging_sites": "integer"
                }
            },
            "validation_rules": {
                "price_min": 5.0,
                "price_max": 100.0,
                "allowed_billing_cycles": ["monthly", "yearly"]
            },
            "template_settings": {
                "default_features": ["Managed WordPress", "SSL Certificates", "Auto-scaling", "24/7 Support"],
                "default_billing_cycle": "monthly"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.hosting_categories.insert_many(default_categories)
    print(f"✅ Created {len(result.inserted_ids)} default categories")

async def create_indexes(db):
    """Create database indexes for better performance"""
    print("📊 Creating database indexes...")
    
    try:
        # Indexes for hosting_categories collection
        await db.hosting_categories.create_index("name", unique=True)
        await db.hosting_categories.create_index("type")
        
        # Indexes for dynamic_plans collection  
        await db.dynamic_plans.create_index("category_id")
        await db.dynamic_plans.create_index("category_type")
        await db.dynamic_plans.create_index("is_active")
        await db.dynamic_plans.create_index([("category_id", 1), ("name", 1)], unique=True)
        
        print("✅ Database indexes created successfully")
        
    except Exception as e:
        print(f"⚠️  Some indexes may already exist: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_to_dynamic_plans())