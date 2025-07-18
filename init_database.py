#!/usr/bin/env python3
"""
Blue Nebula Hosting - Database Initialization Script
This script populates the MongoDB database with default data including hosting plans, content, etc.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

async def init_database(migration_mode=False):
    print("🚀 Initializing Blue Nebula Hosting Database...")
    if migration_mode:
        print("📦 Running in MIGRATION mode - will update existing data safely")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Initialize hosting plans
        await init_hosting_plans(db, migration_mode)
        
        # Initialize website content
        await init_website_content(db, migration_mode)
        
        # Initialize navigation menu
        await init_navigation_menu(db, migration_mode)
        
        # Initialize company info
        await init_company_info(db, migration_mode)
        
        # Initialize legal content
        await init_legal_content(db, migration_mode)
        
        # Initialize site settings
        await init_site_settings(db, migration_mode)
        
        # Initialize SMTP settings
        await init_smtp_settings(db, migration_mode)
        
        # Initialize some sample promo codes
        await init_promo_codes(db, migration_mode)
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        raise
    finally:
        client.close()

async def init_hosting_plans(db, migration_mode=False):
    print("🔧 Setting up hosting plans...")
    
    if migration_mode:
        # In migration mode, only update if no plans exist
        existing_count = await db.hosting_plans.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing hosting plans - skipping initialization")
            return
    
    # Check if plans already exist
    existing_count = await db.hosting_plans.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing plans. Skipping plan initialization.")
        return
    
    hosting_plans = [
        # SSD Shared Hosting (3 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Opal",
            "plan_type": "ssd_shared",
            "price": 1.00,
            "billing_cycle": "monthly",
            "cpu": "1 Core",
            "ram": "1 GB",
            "disk_space": "10 GB SSD",
            "bandwidth": "Unlimited",
            "websites": 1,
            "subdomains": "10",
            "parked_domains": "5",
            "databases": 10,
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=1"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Topaz",
            "plan_type": "ssd_shared",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "2 Core",
            "ram": "2 GB",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited",
            "websites": 5,
            "subdomains": "25",
            "parked_domains": "10",
            "databases": 25,
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=2"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Diamond",
            "plan_type": "ssd_shared",
            "price": 15.00,
            "billing_cycle": "monthly",
            "cpu": "2 Core",
            "ram": "3 GB",
            "disk_space": "100 GB SSD",
            "bandwidth": "Unlimited",
            "websites": "Unlimited",
            "subdomains": "Unlimited",
            "parked_domains": "Unlimited",
            "databases": "Unlimited",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=3"
        },
        
        # HDD Shared Hosting (3 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Quartz",
            "plan_type": "hdd_shared",
            "price": 1.00,
            "billing_cycle": "monthly",
            "cpu": "1 Core",
            "ram": "1 GB",
            "disk_space": "10 GB SSD Storage",
            "bandwidth": "Unlimited Bandwidth",
            "websites": 1,
            "subdomains": "10",
            "parked_domains": "5",
            "databases": 10,
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=4"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Granite",
            "plan_type": "hdd_shared",
            "price": 50.00,
            "billing_cycle": "monthly",
            "cpu": "2 Core",
            "ram": "2 GB",
            "disk_space": "50 GB SSD Storage",
            "bandwidth": "Unlimited Bandwidth",
            "websites": 10,
            "subdomains": "25",
            "parked_domains": "10",
            "databases": 50,
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=5"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marble",
            "plan_type": "hdd_shared",
            "price": 100.00,
            "billing_cycle": "monthly",
            "cpu": "2 Core",
            "ram": "3 GB",
            "disk_space": "100 GB SSD Storage",
            "bandwidth": "Unlimited Bandwidth",
            "websites": "Unlimited",
            "subdomains": "Unlimited",
            "parked_domains": "Unlimited",
            "databases": "Unlimited",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=6"
        },
        
        # Standard VPS (6 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Meteor",
            "plan_type": "standard_vps",
            "price": 1.00,
            "billing_cycle": "monthly",
            "cpu": "1 vCPU",
            "ram": "1 GB RAM",
            "disk_space": "10 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=7"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Asteroid",
            "plan_type": "standard_vps",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "1 vCPU",
            "ram": "2 GB RAM",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=8"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Planet",
            "plan_type": "standard_vps",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "100 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=9"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Star",
            "plan_type": "standard_vps",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "200 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=10"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cluster",
            "plan_type": "standard_vps",
            "price": 80.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "400 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=11"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Galaxy",
            "plan_type": "standard_vps",
            "price": 150.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "800 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=12"
        },
        
        # Performance VPS (9 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Probe",
            "plan_type": "performance_vps",
            "price": 5.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "40 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=13"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rover",
            "plan_type": "performance_vps",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "80 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=14"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lander",
            "plan_type": "performance_vps",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "160 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=15"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Satellite",
            "plan_type": "performance_vps",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "24 GB RAM",
            "disk_space": "320 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=16"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Station",
            "plan_type": "performance_vps",
            "price": 80.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "640 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=17"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Outpost",
            "plan_type": "performance_vps",
            "price": 120.00,
            "billing_cycle": "monthly",
            "cpu": "10 vCPU",
            "ram": "48 GB RAM",
            "disk_space": "960 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=18"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Base",
            "plan_type": "performance_vps",
            "price": 160.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "64 GB RAM",
            "disk_space": "1280 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=19"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Colony",
            "plan_type": "performance_vps",
            "price": 240.00,
            "billing_cycle": "monthly",
            "cpu": "16 vCPU",
            "ram": "96 GB RAM",
            "disk_space": "1920 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=20"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Spaceport",
            "plan_type": "performance_vps",
            "price": 320.00,
            "billing_cycle": "monthly",
            "cpu": "20 vCPU",
            "ram": "128 GB RAM",
            "disk_space": "2560 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "NVMe SSD", "Premium Support", "DDOS Protection"],
            "markup_percentage": 20,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=21"
        },
        
        # Standard GameServer (6 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Stardust",
            "plan_type": "standard_gameserver",
            "price": 5.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "2 GB RAM",
            "disk_space": "20 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "12 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=22"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Flare",
            "plan_type": "standard_gameserver",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "40 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "24 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=23"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Comet",
            "plan_type": "standard_gameserver",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "80 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "48 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=24"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Nova",
            "plan_type": "standard_gameserver",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "12 GB RAM",
            "disk_space": "120 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "64 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=25"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "White Dwarf",
            "plan_type": "standard_gameserver",
            "price": 60.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "160 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "100 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=26"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Red Giant",
            "plan_type": "standard_gameserver",
            "price": 100.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "24 GB RAM",
            "disk_space": "240 GB SSD",
            "bandwidth": "Unlimited",
            "max_players": "150 Players",
            "features": ["Game Panel", "Instant Setup", "DDoS Protection", "24/7 Support"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=27"
        },
        
        # Performance GameServer (9 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Supernova",
            "plan_type": "performance_gameserver",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "40 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "24 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=28"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Neutron Star",
            "plan_type": "performance_gameserver",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "80 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "48 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=29"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pulsar",
            "plan_type": "performance_gameserver",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "12 GB RAM",
            "disk_space": "120 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "64 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=30"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Magnetar",
            "plan_type": "performance_gameserver",
            "price": 60.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "160 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "100 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=31"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Black Hole",
            "plan_type": "performance_gameserver",
            "price": 100.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "24 GB RAM",
            "disk_space": "240 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "150 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=32"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quasar",
            "plan_type": "performance_gameserver",
            "price": 150.00,
            "billing_cycle": "monthly",
            "cpu": "16 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "320 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "200 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=33"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Nebula",
            "plan_type": "performance_gameserver",
            "price": 200.00,
            "billing_cycle": "monthly",
            "cpu": "20 vCPU",
            "ram": "40 GB RAM",
            "disk_space": "400 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "250 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=34"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Star Cluster",
            "plan_type": "performance_gameserver",
            "price": 250.00,
            "billing_cycle": "monthly",
            "cpu": "24 vCPU",
            "ram": "48 GB RAM",
            "disk_space": "480 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "300 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=35"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cosmos",
            "plan_type": "performance_gameserver",
            "price": 300.00,
            "billing_cycle": "monthly",
            "cpu": "32 vCPU",
            "ram": "64 GB RAM",
            "disk_space": "640 GB NVMe SSD",
            "bandwidth": "Unlimited",
            "max_players": "500 Players",
            "features": ["Premium Game Panel", "NVMe Storage", "Priority Support", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=36"
        },
        
        # Custom Shared Hosting - Build Your Own Plan (3 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Custom Basic",
            "plan_type": "custom_shared",
            "price": 5.00,
            "billing_cycle": "monthly",
            "cpu": "Flexible",
            "ram": "Configurable",
            "disk_space": "Custom SSD",
            "bandwidth": "Unlimited",
            "websites": "Custom",
            "subdomains": "Configurable",
            "parked_domains": "Custom",
            "databases": "Configurable",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "24/7 Support",
            "features": ["Build Your Own Plan", "Flexible Resources", "Custom Configuration", "24/7 Support"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=37"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Custom Professional",
            "plan_type": "custom_shared",
            "price": 15.00,
            "billing_cycle": "monthly",
            "cpu": "Flexible",
            "ram": "Configurable",
            "disk_space": "Custom SSD",
            "bandwidth": "Unlimited",
            "websites": "Custom",
            "subdomains": "Configurable",
            "parked_domains": "Custom",
            "databases": "Configurable",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "Priority Support",
            "features": ["Build Your Own Plan", "Flexible Resources", "Custom Configuration", "Priority Support", "Advanced Tools"],
            "markup_percentage": 0,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=38"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Custom Enterprise",
            "plan_type": "custom_shared",
            "price": 25.00,
            "billing_cycle": "monthly",
            "cpu": "Flexible",
            "ram": "Configurable",
            "disk_space": "Custom SSD",
            "bandwidth": "Unlimited",
            "websites": "Custom",
            "subdomains": "Configurable",
            "parked_domains": "Custom",
            "databases": "Configurable",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Hourly Backups",
            "support": "Priority Support",
            "features": ["Build Your Own Plan", "Flexible Resources", "Custom Configuration", "Priority Support", "Advanced Tools", "White Label Options"],
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=39"
        },

        # WordPress Managed Hosting (6 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "WP Starter",
            "plan_type": "wordpress",
            "price": 8.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "2 GB",
            "disk_space": "20 GB SSD",
            "bandwidth": "Unlimited",
            "websites": 1,
            "subdomains": "10",
            "parked_domains": "5",
            "databases": "1 WordPress DB",
            "email_accounts": "10",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "WordPress Expert Support",
            "features": ["Managed WordPress", "Auto Updates", "Security Hardening", "WordPress Expert Support"],
            "container_type": "docker",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["Astra", "GeneratePress", "OceanWP"],
            "wp_plugins": ["Yoast SEO", "WooCommerce", "Elementor", "WP Rocket"],
            "backup_frequency": "daily",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": False,
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=40"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WP Business",
            "plan_type": "wordpress",
            "price": 18.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "4 GB",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited",
            "websites": 3,
            "subdomains": "25",
            "parked_domains": "10",
            "databases": "3 WordPress DBs",
            "email_accounts": "50",
            "ssl_certificate": "Free SSL",
            "backup": "Daily Backups",
            "support": "WordPress Expert Support",
            "features": ["Managed WordPress", "Auto Updates", "Security Hardening", "WordPress Expert Support", "Performance Optimization"],
            "container_type": "docker",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["Astra", "GeneratePress", "OceanWP", "Neve", "Kadence"],
            "wp_plugins": ["Yoast SEO", "WooCommerce", "Elementor", "WP Rocket", "UpdraftPlus", "Wordfence"],
            "backup_frequency": "daily",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": True,
            "markup_percentage": 0,
            "is_popular": True,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=41"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WP Professional",
            "plan_type": "wordpress",
            "price": 35.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "8 GB",
            "disk_space": "100 GB SSD",
            "bandwidth": "Unlimited",
            "websites": 10,
            "subdomains": "50",
            "parked_domains": "25",
            "databases": "10 WordPress DBs",
            "email_accounts": "100",
            "ssl_certificate": "Free SSL",
            "backup": "Hourly Backups",
            "support": "WordPress Expert Support",
            "features": ["Managed WordPress", "Auto Updates", "Security Hardening", "WordPress Expert Support", "Performance Optimization", "White Label"],
            "container_type": "docker",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["Astra", "GeneratePress", "OceanWP", "Neve", "Kadence", "Divi", "Avada"],
            "wp_plugins": ["Yoast SEO", "WooCommerce", "Elementor", "WP Rocket", "UpdraftPlus", "Wordfence", "WP Migrate DB"],
            "backup_frequency": "hourly",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": True,
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=42"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WP Agency",
            "plan_type": "wordpress",
            "price": 55.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "16 GB",
            "disk_space": "200 GB SSD",
            "bandwidth": "Unlimited",
            "websites": "25",
            "subdomains": "100",
            "parked_domains": "50",
            "databases": "25 WordPress DBs",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Hourly Backups",
            "support": "WordPress Expert Support",
            "features": ["Managed WordPress", "Auto Updates", "Security Hardening", "WordPress Expert Support", "Performance Optimization", "White Label", "Agency Tools"],
            "container_type": "kubernetes",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["Astra", "GeneratePress", "OceanWP", "Neve", "Kadence", "Divi", "Avada", "Genesis", "Enfold"],
            "wp_plugins": ["Yoast SEO", "WooCommerce", "Elementor", "WP Rocket", "UpdraftPlus", "Wordfence", "WP Migrate DB", "ManageWP", "MainWP"],
            "backup_frequency": "hourly",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": True,
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=43"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WP Enterprise",
            "plan_type": "wordpress",
            "price": 85.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "32 GB",
            "disk_space": "500 GB SSD",
            "bandwidth": "Unlimited",
            "websites": "50",
            "subdomains": "Unlimited",
            "parked_domains": "Unlimited",
            "databases": "50 WordPress DBs",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Free SSL",
            "backup": "Real-time Backups",
            "support": "Dedicated WordPress Expert",
            "features": ["Managed WordPress", "Auto Updates", "Security Hardening", "Dedicated WordPress Expert", "Performance Optimization", "White Label", "Agency Tools", "Custom Development"],
            "container_type": "kubernetes",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["All Premium Themes Included"],
            "wp_plugins": ["All Premium Plugins Included"],
            "backup_frequency": "real-time",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": True,
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=44"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WP Multisite",
            "plan_type": "wordpress",
            "price": 120.00,
            "billing_cycle": "monthly",
            "cpu": "16 vCPU",
            "ram": "64 GB",
            "disk_space": "1 TB SSD",
            "bandwidth": "Unlimited",
            "websites": "Unlimited Multisite",
            "subdomains": "Unlimited",
            "parked_domains": "Unlimited",
            "databases": "Multisite Network",
            "email_accounts": "Unlimited",
            "ssl_certificate": "Wildcard SSL",
            "backup": "Real-time Backups",
            "support": "Dedicated WordPress Expert",
            "features": ["WordPress Multisite", "Network Management", "Auto Updates", "Security Hardening", "Dedicated WordPress Expert", "Performance Optimization", "White Label", "Custom Development"],
            "container_type": "kubernetes",
            "wp_version": "latest",
            "php_version": "8.3",
            "wp_themes": ["All Premium Themes Included"],
            "wp_plugins": ["All Premium Plugins Included", "Multisite Tools"],
            "backup_frequency": "real-time",
            "ssl_management": "automatic",
            "cdn_included": True,
            "staging_environment": True,
            "markup_percentage": 0,
            "is_popular": False,
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=45"
        }
    ]
    
    result = await db.hosting_plans.insert_many(hosting_plans)
    print(f"✅ Inserted {len(result.inserted_ids)} hosting plans")

async def init_website_content(db, migration_mode=False):
    print("🌐 Initializing website content...")
    
    if migration_mode:
        existing_count = await db.website_content.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing website content items - skipping initialization")
            return
    
    # Check if content already exists
    existing_count = await db.website_content.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing content items. Skipping content initialization.")
        return
    
    website_content = [
        {
            "id": str(uuid.uuid4()),
            "section": "hero",
            "title": "Fast, Reliable, and Affordable",
            "subtitle": "Hosting Solutions—Starting at $1/mo",
            "description": "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions with 24/7 support, 99.9% uptime guarantee, and professional managed services for shared hosting, VPS, and GameServers.",
            "button_text": "Get Started Today",
            "button_url": "https://billing.bluenebulahosting.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "section": "about", 
            "title": "About Blue Nebula Hosting",
            "subtitle": "Your trusted hosting partner since 2020",
            "description": "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions for individuals and businesses. Our managed hosting services include shared hosting, VPS, and GameServers with 24/7 support.\n\nWe pride ourselves on delivering enterprise-grade infrastructure with personal support, ensuring your websites and applications run smoothly while you focus on growing your business.",
            "button_text": "Learn More",
            "button_url": "/about",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "section": "features",
            "title": "Why Choose Blue Nebula?",
            "subtitle": "Professional hosting solutions with enterprise-grade infrastructure and 24/7 expert support",
            "description": "We deliver exceptional hosting services with industry-leading performance, reliability, and support. Our infrastructure is designed to scale with your business needs.",
            "button_text": "View Plans",
            "button_url": "#hosting",
            "features": [
                "99.9% Uptime Guarantee",
                "24/7 Expert Support", 
                "5000+ Happy Customers",
                "Enterprise SSD Storage",
                "Free SSL Certificates",
                "Daily Backups Included"
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.website_content.insert_many(website_content)
    print(f"✅ Inserted {len(result.inserted_ids)} website content items")

async def init_navigation_menu(db, migration_mode=False):
    print("🧭 Initializing navigation menu...")
    
    if migration_mode:
        existing_count = await db.navigation_items.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing navigation items - skipping initialization")
            return
    
    navigation_items = [
        {
            "id": str(uuid.uuid4()),
            "label": "Home",
            "href": "/",
            "order": 1,
            "is_external": False
        },
        {
            "id": str(uuid.uuid4()),
            "label": "Hosting",
            "href": "#hosting",
            "order": 2,
            "is_external": False,
            "dropdown_items": [
                {"label": "Shared Hosting", "href": "#hosting"},
                {"label": "VPS Hosting", "href": "#vps"},
                {"label": "GameServer Hosting", "href": "#gameservers"}
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "label": "About",
            "href": "/about",
            "order": 3,
            "is_external": False
        },
        {
            "id": str(uuid.uuid4()),
            "label": "Contact",
            "href": "/contact",
            "order": 4,
            "is_external": False
        }
    ]
    
    result = await db.navigation_menu.insert_many(navigation_items)
    print(f"✅ Inserted {len(result.inserted_ids)} navigation items")

async def init_company_info(db, migration_mode=False):
    print("🏢 Initializing company info...")
    
    if migration_mode:
        existing_count = await db.company_info.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing company info - skipping initialization")
            return
    
    # Check if company info already exists
    existing = await db.company_info.find_one({})
    if existing:
        print("⚠️  Company info already exists. Skipping initialization.")
        return
    
    company_info = {
        "id": str(uuid.uuid4()),
        "name": "Blue Nebula Hosting",
        "tagline": "Professional hosting solutions with enterprise-grade infrastructure and 24/7 support.",
        "address": "123 Tech Street, Digital City, DC 12345",
        "phone": "+1 (555) 123-4567",
        "email": "support@bluenebulahosting.com",
        "support_email": "support@bluenebulahosting.com",
        "sales_email": "sales@bluenebulahosting.com",
        "website": "https://bluenebulahosting.com",
        "social_media": {
            "twitter": "https://twitter.com/bluenebula",
            "facebook": "https://facebook.com/bluenebulahosting",
            "linkedin": "https://linkedin.com/company/bluenebulahosting"
        }
    }
    
    result = await db.company_info.insert_one(company_info)
    print(f"✅ Inserted company info")

async def init_legal_content(db, migration_mode=False):
    print("⚖️ Initializing legal content...")
    
    if migration_mode:
        existing_count = await db.legal_content.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing legal content - skipping initialization")
            return
    
    # Check if legal content already exists
    existing_count = await db.legal_content.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing legal items. Skipping legal content initialization.")
        return
    
    legal_content = [
        {
            "id": str(uuid.uuid4()),
            "type": "terms",
            "title": "Terms of Service",
            "content": "These Terms of Service govern your use of Blue Nebula Hosting services...",
            "last_updated": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "type": "privacy",
            "title": "Privacy Policy", 
            "content": "This Privacy Policy describes how Blue Nebula Hosting collects, uses, and protects your information...",
            "last_updated": datetime.utcnow()
        }
    ]
    
    result = await db.legal_content.insert_many(legal_content)
    print(f"✅ Inserted {len(result.inserted_ids)} legal content items")

async def init_site_settings(db, migration_mode=False):
    print("⚙️ Initializing site settings...")
    
    if migration_mode:
        existing_count = await db.site_settings.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing site settings - skipping initialization")
            return
    
    # Check if site settings already exist
    existing = await db.site_settings.find_one({})
    if existing:
        print("⚠️  Site settings already exist. Skipping initialization.")
        return
    
    site_settings = {
        "id": str(uuid.uuid4()),
        "site_title": "Blue Nebula Hosting",
        "site_description": "Professional hosting solutions with enterprise-grade infrastructure",
        "maintenance_mode": False,
        "uptime_kuma": {
            "enabled": True,
            "url": "https://status.bluenebulahosting.com",
            "update_interval": 300
        },
        "social_media": {
            "twitter": "https://twitter.com/bluenebula",
            "facebook": "https://facebook.com/bluenebulahosting",
            "linkedin": "https://linkedin.com/company/bluenebulahosting"
        }
    }
    
    result = await db.site_settings.insert_one(site_settings)
    print(f"✅ Inserted site settings")

async def init_smtp_settings(db, migration_mode=False):
    print("📧 Initializing SMTP settings...")
    
    if migration_mode:
        existing_count = await db.smtp_settings.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing SMTP settings - skipping initialization")
            return
    
    # Check if SMTP settings already exist
    existing = await db.smtp_settings.find_one({})
    if existing:
        print("⚠️  SMTP settings already exist. Skipping initialization.")
        return
    
    smtp_settings = {
        "id": str(uuid.uuid4()),
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "noreply@bluenebulahosting.com",
        "password": "",  # Set via environment variable
        "use_tls": True,
        "use_ssl": False,
        "from_email": "noreply@bluenebulahosting.com",
        "from_name": "Blue Nebula Hosting",
        "enabled": False  # Disabled by default until configured
    }
    
    result = await db.smtp_settings.insert_one(smtp_settings)
    print(f"✅ Inserted SMTP settings")

async def init_promo_codes(db, migration_mode=False):
    print("🎁 Setting up sample promo codes...")
    
    if migration_mode:
        existing_count = await db.promo_codes.count_documents({})
        if existing_count > 0:
            print(f"📋 Found {existing_count} existing promo codes - skipping initialization")
            return
    
    # Check if promo codes already exist
    existing_count = await db.promo_codes.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing promo codes. Skipping promo code initialization.")
        return
    
    promo_codes = [
        {
            "id": str(uuid.uuid4()),
            "code": "WELCOME50",
            "title": "Welcome Offer - 50% Off",
            "description": "New customers get 50% off their first hosting plan!",
            "discount_percentage": 50,
            "expiry_date": datetime(2025, 12, 31, 23, 59, 59),
            "is_active": True,
            "display_location": "floating",
            "button_text": "Get Deal Now",
            "button_url": "https://bluenebulahosting.com/billing",
            "created_date": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "SAVE20",
            "title": "Save 20% Today",
            "description": "Limited time offer - 20% off all VPS plans",
            "discount_percentage": 20,
            "expiry_date": datetime(2025, 6, 30, 23, 59, 59),
            "is_active": True,
            "display_location": "hero",
            "button_text": "Copy Code",
            "created_date": datetime.utcnow()
        }
    ]
    
    result = await db.promo_codes.insert_many(promo_codes)
    print(f"✅ Inserted {len(result.inserted_ids)} promo codes")

async def migrate_database():
    """
    Migration function to safely update existing database with new features
    without losing existing data.
    """
    print("🔄 Running database migration...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Check if collections exist and migrate as needed
        collections = await db.list_collection_names()
        print(f"📋 Found existing collections: {collections}")
        
        # Migrate hosting plans if needed
        if "hosting_plans" in collections:
            await migrate_hosting_plans(db)
        
        # Migrate content structures
        if "website_content" in collections:
            await migrate_website_content(db)
        
        # Add missing collections safely
        await init_navigation_menu(db, migration_mode=True)
        await init_smtp_settings(db, migration_mode=True)
        await init_legal_content(db, migration_mode=True)
        
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e
    finally:
        client.close()

async def migrate_hosting_plans(db):
    """Migrate hosting plans to ensure they have all required fields"""
    plans = await db.hosting_plans.find().to_list(1000)
    updated_count = 0
    
    for plan in plans:
        updates = {}
        
        # Ensure all plans have order_url
        if "order_url" not in plan:
            updates["order_url"] = "https://billing.bluenebulahosting.com"
        
        # Migrate old type/sub_type format to plan_type if needed
        if "type" in plan and "sub_type" in plan and "plan_type" not in plan:
            plan_type_map = {
                ("shared", "ssd"): "ssd_shared",
                ("shared", "hdd"): "hdd_shared", 
                ("shared", "custom"): "custom_shared",
                ("vps", "standard"): "standard_vps",
                ("vps", "performance"): "performance_vps",
                ("gameserver", "standard"): "standard_gameserver",
                ("gameserver", "performance"): "performance_gameserver",
                ("wordpress", "managed"): "wordpress",
                ("wordpress", "multisite"): "wordpress"
            }
            
            old_key = (plan.get("type"), plan.get("sub_type"))
            if old_key in plan_type_map:
                updates["plan_type"] = plan_type_map[old_key]
                # Keep the old fields for compatibility during transition
                # They can be removed in a future migration
        
        # Ensure WordPress plans have all WordPress-specific fields with defaults
        if plan.get("plan_type") == "wordpress":
            wp_defaults = {
                "container_type": "docker",
                "wp_version": "latest",
                "php_version": "8.3",
                "wp_themes": [],
                "wp_plugins": [],
                "backup_frequency": "daily",
                "ssl_management": "automatic",
                "cdn_included": True,
                "staging_environment": False
            }
            
            for field, default_value in wp_defaults.items():
                if field not in plan:
                    updates[field] = default_value
        
        # Ensure technical specs exist for non-shared plans
        if plan.get("plan_type") in ["standard_vps", "performance_vps", "standard_gameserver", "performance_gameserver"]:
            if "cpu" not in plan and "cpu_cores" in plan:
                updates["cpu"] = plan["cpu_cores"]
            if "ram" not in plan and "memory_gb" in plan:
                updates["ram"] = plan["memory_gb"]
            if "disk_space" not in plan and "disk_gb" in plan:
                updates["disk_space"] = plan["disk_gb"]
        
        if updates:
            await db.hosting_plans.update_one({"id": plan["id"]}, {"$set": updates})
            updated_count += 1
    
    print(f"✅ Migrated {updated_count} hosting plans")

async def migrate_website_content(db):
    """Migrate website content to ensure proper structure"""
    # Check if content has proper section structure
    content_items = await db.website_content.find().to_list(100)
    
    # Ensure basic sections exist
    required_sections = ["hero", "about", "features"]
    existing_sections = [item.get("section") for item in content_items]
    
    for section in required_sections:
        if section not in existing_sections:
            await db.website_content.insert_one({
                "id": str(uuid.uuid4()),
                "section": section,
                "title": f"Default {section.title()} Title",
                "subtitle": "",
                "description": f"Default {section} content",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            print(f"✅ Created missing {section} content section")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        asyncio.run(migrate_database())
    else:
        asyncio.run(init_database())