#!/usr/bin/env python3
"""
Blue Nebula Hosting - Change Admin Credentials
This script allows you to change the admin login credentials
"""

import asyncio
import hashlib
import getpass
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://admin:secure_password_change_this@localhost:27017/blue_nebula_hosting?authSource=admin')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def change_admin_credentials():
    print("🔐 Blue Nebula Hosting - Change Admin Credentials")
    print("===============================================")
    
    # Get new credentials
    print("\nEnter new admin credentials:")
    new_username = input("New username: ").strip()
    if not new_username:
        print("❌ Username cannot be empty")
        return False
        
    new_password = getpass.getpass("New password: ").strip()
    if not new_password:
        print("❌ Password cannot be empty")
        return False
        
    confirm_password = getpass.getpass("Confirm password: ").strip()
    if new_password != confirm_password:
        print("❌ Passwords do not match")
        return False
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update or create admin user
        admin_user = {
            "username": new_username,
            "password": hashed_password,
            "role": "admin",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        # Remove old admin users and insert new one
        await db.admin_users.delete_many({})
        await db.admin_users.insert_one(admin_user)
        
        print(f"✅ Admin credentials updated successfully!")
        print(f"   Username: {new_username}")
        print(f"   Password: {'*' * len(new_password)}")
        print("\n🌐 You can now login at: https://bluenebulahosting.com/admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating credentials: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(change_admin_credentials())
    if not success:
        exit(1)