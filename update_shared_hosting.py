#!/usr/bin/env python3
"""
Script to add shared hosting specific fields to existing shared hosting plans
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def update_shared_hosting_plans():
    print("🔄 Updating shared hosting plans with specific fields...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Define shared hosting plans with their specific fields
    shared_hosting_updates = {
        # SSD Shared Hosting
        "Opal": {
            "websites": "1",
            "subdomains": "10", 
            "parked_domains": "5",
            "addon_domains": "0",
            "databases": "1",
            "email_accounts": "5"
        },
        "Topaz": {
            "websites": "5",
            "subdomains": "25",
            "parked_domains": "10", 
            "addon_domains": "5",
            "databases": "10",
            "email_accounts": "Unlimited"
        },
        "Diamond": {
            "websites": "Unlimited",
            "subdomains": "Unlimited",
            "parked_domains": "Unlimited",
            "addon_domains": "Unlimited", 
            "databases": "Unlimited",
            "email_accounts": "Unlimited"
        },
        # HDD Shared Hosting  
        "Quartz": {
            "websites": "1",
            "subdomains": "5",
            "parked_domains": "2",
            "addon_domains": "0",
            "databases": "1", 
            "email_accounts": "3"
        },
        "Granite": {
            "websites": "5",
            "subdomains": "15",
            "parked_domains": "5",
            "addon_domains": "3",
            "databases": "5",
            "email_accounts": "25"
        },
        "Marble": {
            "websites": "Unlimited",
            "subdomains": "Unlimited", 
            "parked_domains": "Unlimited",
            "addon_domains": "Unlimited",
            "databases": "Unlimited",
            "email_accounts": "Unlimited"
        }
    }
    
    # Update each shared hosting plan
    for plan_name, fields in shared_hosting_updates.items():
        try:
            result = await db.hosting_plans.update_one(
                {"name": plan_name},
                {"$set": fields}
            )
            if result.modified_count > 0:
                print(f"✅ Updated {plan_name} with shared hosting fields")
            else:
                print(f"⚠️  {plan_name} not found or already updated")
        except Exception as e:
            print(f"❌ Error updating {plan_name}: {e}")
    
    print("🎉 Shared hosting plan updates completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(update_shared_hosting_plans())