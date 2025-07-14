#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_content():
    MONGO_URL = "mongodb://localhost:27017"
    DB_NAME = "test_database"
    
    print(f"Connecting to: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Check what collections exist
        collections = await db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Check website_content
        content_items = await db.website_content.find().to_list(100)
        print(f"\nWebsite content items: {len(content_items)}")
        for item in content_items:
            if "_id" in item:
                del item["_id"]
            print(f"- {item.get('section', 'unknown')}: {item.get('title', 'No title')}")
        
        # Check specifically for hero content
        hero_content = await db.website_content.find_one({"section": "hero"})
        if hero_content:
            if "_id" in hero_content:
                del hero_content["_id"]
            print(f"\nHero content found: {hero_content}")
        else:
            print("\nNo hero content found in database")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_content())
