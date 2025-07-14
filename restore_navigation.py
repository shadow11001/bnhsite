#!/usr/bin/env python3
"""
Script to restore original navigation in the correct collection
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def restore_navigation():
    print("🔄 Restoring original navigation in navigation_items collection...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Clear existing navigation items
    await db.navigation_items.delete_many({})
    
    # Insert original navigation items
    original_navigation = [
        {"label": "Home", "href": "/", "order": 1, "is_external": False, "id": "nav-home"},
        {"label": "About", "href": "#about", "order": 2, "is_external": False, "id": "nav-about"},
        {"label": "Hosting", "href": "#hosting", "order": 3, "is_external": False, "id": "nav-hosting"},
        {"label": "Contact", "href": "#contact", "order": 4, "is_external": False, "id": "nav-contact"}
    ]
    
    try:
        await db.navigation_items.insert_many(original_navigation)
        print("✅ Navigation items restored in navigation_items collection")
    except Exception as e:
        print(f"❌ Error restoring navigation: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(restore_navigation())