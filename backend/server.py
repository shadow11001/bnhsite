from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Blue Nebula Hosting API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class HostingPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_type: str  # "ssd_shared", "hdd_shared", "standard_vps", "performance_vps", "standard_gameserver", "performance_gameserver"
    plan_name: str
    base_price: float
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    disk_type: str = "SSD"  # "SSD" or "HDD"
    bandwidth: Optional[str] = None
    supported_games: Optional[List[str]] = None
    features: List[str] = []
    popular: bool = False
    markup_percentage: int = 0

class CompanyInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Blue Nebula Hosting"
    tagline: str = "Fast, Reliable, and Affordable Hosting Solutions"
    description: str
    founded_year: int = 2020
    features: List[str] = []

class ContactInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    subject: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Blue Nebula Hosting API", "status": "online"}

@api_router.get("/hosting-plans", response_model=List[HostingPlan])
async def get_hosting_plans(plan_type: Optional[str] = None):
    """Get all hosting plans or filter by type"""
    try:
        query = {}
        if plan_type:
            query["plan_type"] = plan_type
        
        plans = await db.hosting_plans.find(query).to_list(1000)
        return [HostingPlan(**plan) for plan in plans]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/hosting-plans/{plan_id}", response_model=HostingPlan)
async def get_hosting_plan(plan_id: str):
    """Get specific hosting plan by ID"""
    try:
        plan = await db.hosting_plans.find_one({"id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return HostingPlan(**plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/company-info", response_model=CompanyInfo)
async def get_company_info():
    """Get company information"""
    try:
        company = await db.company_info.find_one()
        if not company:
            # Return default company info if none exists
            default_info = CompanyInfo(
                description="Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions for individuals and businesses. Our managed hosting services include shared hosting, VPS, and GameServer hosting with 24/7 support.",
                features=[
                    "24/7 Expert Support",
                    "99.9% Uptime Guarantee", 
                    "Free SSL Certificates",
                    "Daily Automated Backups",
                    "DDoS Protection",
                    "One-Click App Installations",
                    "cPanel/HestiaCP Control Panel",
                    "Pterodactyl Game Panel",
                    "30-Day Money Back Guarantee"
                ]
            )
            return default_info
        return CompanyInfo(**company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/contact", response_model=ContactInfo)
async def submit_contact(contact: ContactInfo):
    """Submit contact form"""
    try:
        contact_dict = contact.dict()
        await db.contact_submissions.insert_one(contact_dict)
        return contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/features")
async def get_features():
    """Get hosting features and benefits"""
    return {
        "shared_hosting_features": [
            "Free Domain for 1st Year",
            "Unlimited Bandwidth",
            "Free SSL Certificate",
            "Daily Backups",
            "99.9% Uptime Guarantee",
            "24/7 Support",
            "One-Click WordPress Install",
            "HestiaCP Control Panel"
        ],
        "vps_features": [
            "Full Root Access",
            "Choice of Operating System", 
            "Dedicated IP Address",
            "SSD Storage",
            "DDoS Protection",
            "24/7 Monitoring",
            "Scalable Resources",
            "Managed Support"
        ],
        "gameserver_features": [
            "Instant Setup",
            "Pterodactyl Control Panel",
            "DDoS Protection",
            "High-Performance Hardware",
            "Multiple Game Support",
            "Automatic Backups",
            "24/7 Support",
            "Custom Configurations"
        ]
    }

# Initialize hosting plans data
@api_router.post("/init-data")
async def initialize_data():
    """Initialize hosting plans data - for development only"""
    try:
        # Clear existing data
        await db.hosting_plans.delete_many({})
        
        # SSD Shared Hosting Plans
        ssd_shared_plans = [
            {
                "plan_type": "ssd_shared",
                "plan_name": "Opal",
                "base_price": 1.0,
                "disk_gb": 10,
                "disk_type": "SSD",
                "features": ["1 Website", "10 GB SSD Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups"],
                "popular": False
            },
            {
                "plan_type": "ssd_shared", 
                "plan_name": "Topaz",
                "base_price": 10.0,
                "disk_gb": 50,
                "disk_type": "SSD", 
                "features": ["10 Websites", "50 GB SSD Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups"],
                "popular": True
            },
            {
                "plan_type": "ssd_shared",
                "plan_name": "Diamond", 
                "base_price": 15.0,
                "disk_gb": 100,
                "disk_type": "SSD",
                "features": ["Unlimited Websites", "100 GB SSD Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups", "Priority Support"],
                "popular": False
            }
        ]
        
        # HDD Shared Hosting Plans  
        hdd_shared_plans = [
            {
                "plan_type": "hdd_shared",
                "plan_name": "Quartz",
                "base_price": 2.0,
                "disk_gb": 25,
                "disk_type": "HDD",
                "features": ["5 Websites", "25 GB Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups"],
                "popular": False
            },
            {
                "plan_type": "hdd_shared",
                "plan_name": "Emerald", 
                "base_price": 3.0,
                "disk_gb": 50,
                "disk_type": "HDD",
                "features": ["15 Websites", "50 GB Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups"],
                "popular": False
            },
            {
                "plan_type": "hdd_shared",
                "plan_name": "Marble",
                "base_price": 5.0, 
                "disk_gb": 100,
                "disk_type": "HDD",
                "features": ["Unlimited Websites", "100 GB Storage", "Unlimited Bandwidth", "Free SSL", "Daily Backups"],
                "popular": False
            }
        ]
        
        # Standard VPS Plans (20% markup)
        standard_vps_plans = [
            {
                "plan_type": "standard_vps",
                "plan_name": "Mercury",
                "base_price": 10.0,
                "cpu_cores": 1,
                "memory_gb": 2,
                "disk_gb": 55,
                "disk_type": "SSD",
                "markup_percentage": 20,
                "features": ["1 vCPU", "2 GB RAM", "55 GB SSD", "Root Access", "Choice of OS"],
                "popular": False
            },
            {
                "plan_type": "standard_vps", 
                "plan_name": "Venus",
                "base_price": 20.0,
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 80,
                "disk_type": "SSD",
                "markup_percentage": 20,
                "features": ["2 vCPU", "4 GB RAM", "80 GB SSD", "Root Access", "Choice of OS"],
                "popular": True
            },
            {
                "plan_type": "standard_vps",
                "plan_name": "Earth", 
                "base_price": 40.0,
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_gb": 160,
                "disk_type": "SSD", 
                "markup_percentage": 20,
                "features": ["4 vCPU", "8 GB RAM", "160 GB SSD", "Root Access", "Choice of OS"],
                "popular": False
            }
        ]
        
        # Standard GameServer Plans (40% markup)
        gameserver_plans = [
            {
                "plan_type": "standard_gameserver",
                "plan_name": "Lunar",
                "base_price": 10.0,
                "cpu_cores": 1,
                "memory_gb": 2,
                "disk_gb": 25,
                "disk_type": "SSD",
                "markup_percentage": 40,
                "supported_games": ["Minecraft", "Terraria", "Garry's Mod"],
                "features": ["1 vCPU", "2 GB RAM", "25 GB SSD", "Pterodactyl Panel", "DDoS Protection"],
                "popular": False
            },
            {
                "plan_type": "standard_gameserver",
                "plan_name": "Solar", 
                "base_price": 20.0,
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 80,
                "disk_type": "SSD",
                "markup_percentage": 40,
                "supported_games": ["Minecraft", "CS:GO", "TF2", "ARK"],
                "features": ["2 vCPU", "4 GB RAM", "80 GB SSD", "Pterodactyl Panel", "DDoS Protection"],
                "popular": True
            },
            {
                "plan_type": "standard_gameserver",
                "plan_name": "Galactic",
                "base_price": 80.0,
                "cpu_cores": 6,
                "memory_gb": 16,
                "disk_gb": 320,
                "disk_type": "SSD",
                "markup_percentage": 40,
                "supported_games": ["Minecraft", "Rust", "CS:GO", "TF2", "ARK", "Terraria"],
                "features": ["6 vCPU", "16 GB RAM", "320 GB SSD", "Pterodactyl Panel", "DDoS Protection", "Priority Support"],
                "popular": False
            }
        ]
        
        # Combine all plans
        all_plans = ssd_shared_plans + hdd_shared_plans + standard_vps_plans + gameserver_plans
        
        # Add IDs to all plans
        for plan in all_plans:
            plan["id"] = str(uuid.uuid4())
        
        # Insert all plans
        await db.hosting_plans.insert_many(all_plans)
        
        return {"message": f"Initialized {len(all_plans)} hosting plans successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()