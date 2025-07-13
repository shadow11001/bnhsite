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
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@bnhsite-mongodb:27017/blue_nebula_hosting?authSource=admin')
DB_NAME = os.environ.get('DB_NAME', 'blue_nebula_hosting')

async def init_database():
    print("🚀 Initializing Blue Nebula Hosting Database...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Initialize hosting plans
        await init_hosting_plans(db)
        
        # Initialize website content
        await init_website_content(db)
        
        # Initialize navigation menu
        await init_navigation_menu(db)
        
        # Initialize company info
        await init_company_info(db)
        
        # Initialize legal content
        await init_legal_content(db)
        
        # Initialize site settings
        await init_site_settings(db)
        
        # Initialize SMTP settings
        await init_smtp_settings(db)
        
        # Initialize some sample promo codes
        await init_promo_codes(db)
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        return False
    finally:
        client.close()
    
    return True

async def init_hosting_plans(db):
    print("📊 Initializing hosting plans...")
    
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
            "type": "shared",
            "sub_type": "ssd",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=1"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Topaz",
            "type": "shared",
            "sub_type": "ssd",
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
            "type": "shared",
            "sub_type": "ssd",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=3"
        },
        
        # HDD Shared Hosting (3 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Quartz",
            "type": "shared",
            "sub_type": "hdd",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=4"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Granite",
            "type": "shared",
            "sub_type": "hdd",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=5"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marble",
            "type": "shared",
            "sub_type": "hdd",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=6"
        },
        
        # Standard VPS (6 plans)
        {
            "id": str(uuid.uuid4()),
            "name": "Meteor",
            "type": "vps",
            "sub_type": "standard",
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
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=7"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Asteroid",
            "type": "vps",
            "sub_type": "standard",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Planet",
            "type": "vps",
            "sub_type": "standard",
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
            "is_popular": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Star",
            "type": "vps",
            "sub_type": "standard",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cluster",
            "type": "vps",
            "sub_type": "standard",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Galaxy",
            "type": "vps",
            "sub_type": "standard",
            "price": 160.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "800 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        }
    ]
    
    # Add Performance VPS plans (9 plans)
    performance_vps_plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "Probe",
            "type": "vps",
            "sub_type": "performance",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rover",
            "type": "vps",
            "sub_type": "performance",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lander",
            "type": "vps",
            "sub_type": "performance",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Satellite",
            "type": "vps",
            "sub_type": "performance",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Station",
            "type": "vps",
            "sub_type": "performance",
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
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Outpost",
            "type": "vps",
            "sub_type": "performance",
            "price": 160.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "800 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Base",
            "type": "vps",
            "sub_type": "performance",
            "price": 320.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "64 GB RAM",
            "disk_space": "1600 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Colony",
            "type": "vps",
            "sub_type": "performance",
            "price": 640.00,
            "billing_cycle": "monthly",
            "cpu": "16 vCPU",
            "ram": "128 GB RAM",
            "disk_space": "3200 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Spaceport",
            "type": "vps",
            "sub_type": "performance",
            "price": 1280.00,
            "billing_cycle": "monthly",
            "cpu": "24 vCPU",
            "ram": "256 GB RAM",
            "disk_space": "6400 GB SSD",
            "bandwidth": "Unlimited",
            "ip_addresses": "1 Dedicated IP",
            "os_choices": "Multiple OS",
            "features": ["Full Root Access", "Choice of OS", "DDOS Protection", "Scalable Resources"],
            "markup_percentage": 20,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        }
    ]
    
    hosting_plans.extend(performance_vps_plans)
    
    # Add Standard GameServers (6 plans)
    standard_gameserver_plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "Stardust",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 1.00,
            "billing_cycle": "monthly",
            "cpu": "1 vCPU",
            "ram": "1 GB RAM",
            "disk_space": "10 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 8 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Flare",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "2 GB RAM",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 16 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Comet",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "100 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 32 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Nova",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "200 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 64 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "White Dwarf",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 80.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "400 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 128 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Red Giant",
            "type": "gameserver",
            "sub_type": "standard",
            "price": 160.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "800 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 256 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        }
    ]
    
    hosting_plans.extend(standard_gameserver_plans)
    
    # Add Performance GameServers (9 plans)
    performance_gameserver_plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "Supernova",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 1.00,
            "billing_cycle": "monthly",
            "cpu": "1 vCPU",
            "ram": "1 GB RAM",
            "disk_space": "10 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 8 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Neutron Star",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 10.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "2 GB RAM",
            "disk_space": "50 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 16 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pulsar",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 20.00,
            "billing_cycle": "monthly",
            "cpu": "2 vCPU",
            "ram": "4 GB RAM",
            "disk_space": "100 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 32 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Magnetar",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 40.00,
            "billing_cycle": "monthly",
            "cpu": "4 vCPU",
            "ram": "8 GB RAM",
            "disk_space": "200 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 64 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Black Hole",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 80.00,
            "billing_cycle": "monthly",
            "cpu": "6 vCPU",
            "ram": "16 GB RAM",
            "disk_space": "400 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 128 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quasar",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 160.00,
            "billing_cycle": "monthly",
            "cpu": "8 vCPU",
            "ram": "32 GB RAM",
            "disk_space": "800 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 256 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Nebula",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 320.00,
            "billing_cycle": "monthly",
            "cpu": "12 vCPU",
            "ram": "64 GB RAM",
            "disk_space": "1600 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 512 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Star Cluster",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 640.00,
            "billing_cycle": "monthly",
            "cpu": "16 vCPU",
            "ram": "128 GB RAM",
            "disk_space": "3200 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 1024 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cosmos",
            "type": "gameserver",
            "sub_type": "performance",
            "price": 1280.00,
            "billing_cycle": "monthly",
            "cpu": "24 vCPU",
            "ram": "256 GB RAM",
            "disk_space": "6400 GB SSD",
            "bandwidth": "Unlimited",
            "players": "Up to 2048 players",
            "features": ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
            "markup_percentage": 40,
            "is_popular": False
            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid=NEW_ID"
        }
    ]
    
    hosting_plans.extend(performance_gameserver_plans)
    
    # Insert all plans
    result = await db.hosting_plans.insert_many(hosting_plans)
    print(f"✅ Inserted {len(result.inserted_ids)} hosting plans")

async def init_website_content(db):
    print("🌐 Initializing website content...")
    
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

async def init_navigation_menu(db):
    print("🧭 Initializing navigation menu...")
    
    # Check if navigation already exists
    existing_count = await db.navigation_menu.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing navigation items. Skipping navigation initialization.")
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
            "href": "#",
            "order": 2,
            "is_external": False,
            "dropdown_items": [
                {"label": "Shared Hosting", "href": "/hosting/shared"},
                {"label": "VPS Hosting", "href": "/hosting/vps"},
                {"label": "GameServers", "href": "/hosting/gameservers"}
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

async def init_company_info(db):
    print("🏢 Initializing company info...")
    
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

async def init_legal_content(db):
    print("⚖️ Initializing legal content...")
    
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
            "content": "Welcome to Blue Nebula Hosting. By using our services, you agree to these terms.\n\n1. Service Agreement\nBy purchasing our hosting services, you agree to our terms and conditions.\n\n2. Acceptable Use\nYou agree to use our services in accordance with applicable laws and regulations.\n\n3. Payment Terms\nAll payments are due in advance according to your chosen billing cycle.\n\n4. Limitation of Liability\nBlue Nebula Hosting provides services 'as is' without warranty.\n\nFor complete terms, please contact our support team.",
            "last_updated": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "type": "privacy",
            "title": "Privacy Policy",
            "content": "Blue Nebula Hosting respects your privacy and is committed to protecting your personal information.\n\n1. Information We Collect\nWe collect information necessary to provide our hosting services.\n\n2. How We Use Information\nWe use your information to deliver and improve our services.\n\n3. Information Sharing\nWe do not sell or share your personal information with third parties except as required by law.\n\n4. Data Security\nWe implement appropriate security measures to protect your information.\n\n5. Contact Us\nIf you have questions about this policy, please contact us at privacy@bluenebulahosting.com",
            "last_updated": datetime.utcnow()
        }
    ]
    
    result = await db.legal_content.insert_many(legal_content)
    print(f"✅ Inserted {len(result.inserted_ids)} legal content items")

async def init_site_settings(db):
    print("⚙️ Initializing site settings...")
    
    # Check if settings already exist
    existing = await db.site_settings.find_one({})
    if existing:
        print("⚠️  Site settings already exist. Skipping initialization.")
        return
    
    site_settings = {
        "id": str(uuid.uuid4()),
        "site_name": "Blue Nebula Hosting",
        "site_description": "Professional hosting solutions with enterprise-grade infrastructure and 24/7 support",
        "contact_email": "support@bluenebulahosting.com",
        "support_phone": "+1 (555) 123-4567",
        "business_hours": "24/7 Support Available",
        "maintenance_mode": False,
        "analytics_code": "",
        "footer_text": "© 2025 Blue Nebula Hosting. All rights reserved.",
        "social_links": {
            "twitter": "https://twitter.com/bluenebula",
            "facebook": "https://facebook.com/bluenebulahosting",
            "linkedin": "https://linkedin.com/company/bluenebulahosting"
        }
    }
    
    result = await db.site_settings.insert_one(site_settings)
    print(f"✅ Inserted site settings")


async def init_smtp_settings(db):
    print("📧 Initializing SMTP settings...")
    
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

async def init_promo_codes(db):
    print("🎁 Initializing sample promo codes...")
    
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

if __name__ == "__main__":
    asyncio.run(init_database())