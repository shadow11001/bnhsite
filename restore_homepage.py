#!/usr/bin/env python3
"""
Script to restore original homepage content and navigation
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def restore_original_content():
    print("🔄 Restoring original homepage content...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # 1. Restore original navigation menu
    original_navigation = [
        {"label": "Home", "href": "/", "order": 1, "is_external": False, "id": "nav-home"},
        {"label": "About", "href": "#about", "order": 2, "is_external": False, "id": "nav-about"},
        {"label": "Hosting", "href": "#hosting", "order": 3, "is_external": False, "id": "nav-hosting"},
        {"label": "Contact", "href": "#contact", "order": 4, "is_external": False, "id": "nav-contact"}
    ]
    
    try:
        await db.website_content.update_one(
            {"section": "navigation"},
            {"$set": {"content": original_navigation}},
            upsert=True
        )
        print("✅ Navigation menu restored to original")
    except Exception as e:
        print(f"❌ Error restoring navigation: {e}")
    
    # 2. Restore original hero section content
    original_hero = {
        "title": "Professional Web Hosting Solutions",
        "subtitle": "Reliable, Fast, and Secure Hosting for Your Business",
        "description": "Get your website online with our premium hosting services. 99.9% uptime guarantee, 24/7 support, and cutting-edge technology.",
        "cta_primary": "Get Started",
        "cta_secondary": "View Plans"
    }
    
    try:
        await db.website_content.update_one(
            {"section": "hero"},
            {"$set": {"content": original_hero}},
            upsert=True
        )
        print("✅ Hero section restored to original")
    except Exception as e:
        print(f"❌ Error restoring hero: {e}")
    
    # 3. Restore original about section content
    original_about = {
        "title": "About Blue Nebula Hosting",
        "content": "Blue Nebula Hosting provides premium web hosting solutions designed for businesses of all sizes. With our state-of-the-art infrastructure and dedicated support team, we ensure your website stays online and performs at its best.",
        "features": [
            "99.9% Uptime Guarantee",
            "24/7 Technical Support", 
            "Advanced Security Features",
            "Scalable Solutions"
        ]
    }
    
    try:
        await db.website_content.update_one(
            {"section": "about"},
            {"$set": {"content": original_about}},
            upsert=True
        )
        print("✅ About section restored to original")
    except Exception as e:
        print(f"❌ Error restoring about: {e}")
    
    # 4. Restore original features section content
    original_features = {
        "title": "Why Choose Blue Nebula Hosting?",
        "subtitle": "Experience the difference with our premium hosting features",
        "features": [
            {
                "title": "Lightning Fast Performance",
                "description": "SSD storage and optimized servers ensure your website loads quickly",
                "icon": "⚡"
            },
            {
                "title": "24/7 Expert Support", 
                "description": "Our technical support team is available around the clock to help you",
                "icon": "🛠️"
            },
            {
                "title": "Advanced Security",
                "description": "Protect your website with our comprehensive security measures",
                "icon": "🔒"
            }
        ]
    }
    
    try:
        await db.website_content.update_one(
            {"section": "features"},
            {"$set": {"content": original_features}},
            upsert=True
        )
        print("✅ Features section restored to original")
    except Exception as e:
        print(f"❌ Error restoring features: {e}")
    
    print("🎉 Homepage content restoration completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(restore_original_content())