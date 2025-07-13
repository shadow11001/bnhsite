from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import hashlib
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@bnhsite-mongodb:27017/blue_nebula_hosting?authSource=admin')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'blue_nebula_hosting')]

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Blue Nebula Hosting API", version="1.0.0")

# Create a router without prefix (Caddy will handle the /api routing)
api_router = APIRouter()


# Define Models
class SiteSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uptime_kuma_api_key: str
    uptime_kuma_url: str
    status_update_interval: int = 30
    site_title: str
    site_description: str

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

class PublicHostingPlan(BaseModel):
    """Public-facing hosting plan model without internal markup information"""
    id: str
    plan_type: str
    plan_name: str
    base_price: float
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    disk_type: str = "SSD"
    bandwidth: Optional[str] = None
    supported_games: Optional[List[str]] = None
    features: List[str] = []
    popular: bool = False

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

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ContentUpdate(BaseModel):
    section: str  # "hero", "features", "about", "company"
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None

class NavigationItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    href: str
    order: int
    dropdown_items: Optional[List[dict]] = None
    is_external: bool = False

class SMTPSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    from_email: str
    from_name: str

class LegalContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "terms" or "privacy"
    title: str
    content: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PromoCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    title: str
    description: str
    discount_percentage: Optional[int] = None
    discount_amount: Optional[float] = None
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    display_location: str = "hero"  # "hero", "pricing", "floating", "footer"
    button_text: str = "Copy Code"
    button_url: Optional[str] = None  # If provided, button links to URL instead of copying code
    created_date: datetime = Field(default_factory=datetime.utcnow)

# Authentication functions
def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Here you could check if user exists in database
    # For now, we'll just return the username
    return username

# Default admin credentials (change these!)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = hash_password("admin123")  # Change this!

# Uptime Kuma Configuration
UPTIME_KUMA_API_KEY = "uk1_USvIQkci-6cYMA5VcOksKY7B1TzT7ul2zrvFOniq"
UPTIME_KUMA_BASE_URL = "https://status.bluenebulahosting.com"

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Blue Nebula Hosting API", "status": "online"}

@api_router.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Admin login endpoint"""
    try:
        # Check database for admin user
        admin_user = await db.admin_users.find_one({"username": login_request.username})
        
        if admin_user and verify_password(login_request.password, admin_user["password"]):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": login_request.username}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/verify-token")
async def verify_token(current_user: str = Depends(get_current_user)):
    """Verify if token is valid"""
    return {"valid": True, "user": current_user}

# Promo Code Management
@api_router.get("/promo-codes")
async def get_promo_codes():
    """Get all active promo codes"""
    try:
        promo_codes = await db.promo_codes.find({"is_active": True}).to_list(100)
        # Convert ObjectIds to strings for JSON serialization
        for promo in promo_codes:
            if "_id" in promo:
                del promo["_id"]  # Remove MongoDB ObjectId
        return promo_codes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/promo-codes")
async def get_admin_promo_codes(current_user: str = Depends(get_current_user)):
    """Get all promo codes for admin - includes inactive"""
    try:
        promo_codes = await db.promo_codes.find().to_list(100)
        # Convert ObjectIds to strings for JSON serialization
        for promo in promo_codes:
            if "_id" in promo:
                del promo["_id"]  # Remove MongoDB ObjectId
        return promo_codes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/promo-codes")
async def create_promo_code(promo_data: dict, current_user: str = Depends(get_current_user)):
    """Create new promo code - admin only"""
    try:
        # Ensure we use string ID, not ObjectId
        promo_data["id"] = str(uuid.uuid4())
        promo_data["created_date"] = datetime.utcnow().isoformat()
        
        # Remove any _id field to avoid conflicts
        if "_id" in promo_data:
            del promo_data["_id"]
        
        await db.promo_codes.insert_one(promo_data)
        return {"message": "Promo code created successfully", "id": promo_data["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/promo-codes/{promo_id}")
async def update_promo_code(promo_id: str, promo_data: dict, current_user: str = Depends(get_current_user)):
    """Update promo code - admin only"""
    try:
        # Remove any _id field to avoid conflicts
        if "_id" in promo_data:
            del promo_data["_id"]
            
        await db.promo_codes.update_one(
            {"id": promo_id},
            {"$set": promo_data}
        )
        return {"message": "Promo code updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/admin/promo-codes/{promo_id}")
async def delete_promo_code(promo_id: str, current_user: str = Depends(get_current_user)):
    """Delete promo code - admin only"""
    try:
        result = await db.promo_codes.delete_one({"id": promo_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Promo code not found")
        return {"message": "Promo code deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Site Settings Management
@api_router.get("/site-settings")
async def get_site_settings(current_user: str = Depends(get_current_user)):
    """Get site settings - admin only"""
    try:
        settings = await db.site_settings.find_one()
        if not settings:
            return {
                "uptime_kuma_api_key": UPTIME_KUMA_API_KEY,
                "uptime_kuma_url": f"{UPTIME_KUMA_BASE_URL}/status/bnh",
                "status_update_interval": 30,
                "site_title": "Blue Nebula Hosting",
                "site_description": "Professional hosting solutions with enterprise-grade infrastructure"
            }
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/site-settings")
async def update_site_settings(settings_data: dict, current_user: str = Depends(get_current_user)):
    """Update site settings - admin only"""
    try:
        await db.site_settings.update_one(
            {},
            {"$set": settings_data},
            upsert=True
        )
        return {"message": "Site settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/hosting-plans")
async def get_admin_hosting_plans(current_user: str = Depends(get_current_user)):
    """Get all hosting plans with markup data - admin only"""
    try:
        plans = await db.hosting_plans.find().to_list(1000)
        # Convert ObjectIds to strings for JSON serialization
        # Also map old field names to new field names for frontend compatibility
        mapped_plans = []
        for plan in plans:
            if "_id" in plan:
                del plan["_id"]
            
            # Map old field names to new field names for frontend compatibility
            mapped_plan = {}
            for key, value in plan.items():
                if key == "plan_type":
                    mapped_plan["type"] = value
                elif key == "plan_name":
                    mapped_plan["name"] = value
                elif key == "base_price":
                    mapped_plan["price"] = value
                elif key == "popular":
                    mapped_plan["is_popular"] = value
                else:
                    mapped_plan[key] = value
            
            mapped_plans.append(mapped_plan)
        
        return mapped_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/hosting-plans", response_model=List[dict])
async def get_hosting_plans(plan_type: Optional[str] = None):
    """Get all hosting plans or filter by type"""
    try:
        query = {}
        if plan_type:
            query["plan_type"] = plan_type  # Fixed: database field is 'plan_type' not 'type'
        
        plans = await db.hosting_plans.find(query).to_list(1000)
        
        # Convert ObjectIds to strings and return clean data without markup_percentage
        # Also map old field names to new field names expected by frontend
        public_plans = []
        for plan in plans:
            if "_id" in plan:
                del plan["_id"]
            # Remove markup_percentage for public API
            if "markup_percentage" in plan:
                del plan["markup_percentage"]
            
            # Map old field names to new field names for frontend compatibility
            mapped_plan = {}
            for key, value in plan.items():
                if key == "plan_type":
                    mapped_plan["type"] = value
                elif key == "plan_name":
                    mapped_plan["name"] = value
                elif key == "base_price":
                    mapped_plan["price"] = value
                elif key == "popular":
                    mapped_plan["is_popular"] = value
                else:
                    mapped_plan[key] = value
            
            public_plans.append(mapped_plan)
        
        return public_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/hosting-plans/{plan_id}")
async def get_hosting_plan(plan_id: str):
    """Get specific hosting plan by ID"""
    try:
        plan = await db.hosting_plans.find_one({"id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Remove internal fields for public API
        if "_id" in plan:
            del plan["_id"]
        if "markup_percentage" in plan:
            del plan["markup_percentage"]
        
        # Map old field names to new field names for frontend compatibility
        mapped_plan = {}
        for key, value in plan.items():
            if key == "plan_type":
                mapped_plan["type"] = value
            elif key == "plan_name":
                mapped_plan["name"] = value
            elif key == "base_price":
                mapped_plan["price"] = value
            elif key == "popular":
                mapped_plan["is_popular"] = value
            else:
                mapped_plan[key] = value
        
        return mapped_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/hosting-plans/{plan_id}")
async def update_hosting_plan(plan_id: str, plan_update: dict, current_user: str = Depends(get_current_user)):
    """Update hosting plan - for admin use"""
    try:
        # Map frontend field names back to database field names
        db_update = {}
        for key, value in plan_update.items():
            if key == "type":
                db_update["plan_type"] = value
            elif key == "name":
                db_update["plan_name"] = value
            elif key == "price":
                db_update["base_price"] = value
            elif key == "is_popular":
                db_update["popular"] = value
            else:
                db_update[key] = value
        
        result = await db.hosting_plans.update_one(
            {"id": plan_id}, 
            {"$set": db_update}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"message": "Plan updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/company-info", response_model=CompanyInfo)
async def get_company_info():
    """Get company information"""
    try:
        company = await db.company_info.find_one()
        if not company:
            # Return default company information
            return {
                "id": str(uuid.uuid4()),
                "name": "Blue Nebula Hosting",
                "tagline": "Fast, Reliable, and Affordable Hosting Solutions",
                "description": "Blue Nebula Hosting is a premier web hosting provider offering reliable, affordable hosting solutions for businesses of all sizes. We specialize in shared hosting, VPS hosting, and GameServer hosting with enterprise-grade infrastructure, 99.9% uptime guarantee, and 24/7 expert support. Our mission is to empower businesses with robust hosting solutions that scale with their growth.",
                "founded_year": 2020,
                "features": [
                    "99.9% Uptime Guarantee",
                    "24/7 Expert Technical Support",
                    "Enterprise-Grade Security", 
                    "Lightning-Fast SSD Storage",
                    "Free SSL Certificates",
                    "Daily Automated Backups",
                    "DDoS Protection",
                    "Easy One-Click Installations"
                ],
                "contact_email": "support@bluenebulahosting.com",
                "phone": "+1 (555) 123-4567",
                "address": "123 Tech Street, Cloud City, CC 12345"
            }
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/company-info")
async def update_company_info(company_update: dict, current_user: str = Depends(get_current_user)):
    """Update company information - for admin use"""
    try:
        await db.company_info.update_one(
            {}, 
            {"$set": company_update}, 
            upsert=True
        )
        return {"message": "Company info updated successfully"}
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

@api_router.put("/content")
async def update_content(content_update: ContentUpdate, current_user: str = Depends(get_current_user)):
    """Update website content - for admin use"""
    try:
        update_data = content_update.dict(exclude_unset=True)
        await db.website_content.update_one(
            {"section": content_update.section},
            {"$set": update_data},
            upsert=True
        )
        return {"message": f"Content for {content_update.section} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content/{section}")
async def get_content(section: str):
    """Get website content by section"""
    try:
        content = await db.website_content.find_one({"section": section})
        if not content:
            # Return default content for legal pages
            if section == "terms":
                return {
                    "section": "terms",
                    "title": "Terms of Service",
                    "content": "Terms of Service content will be updated by the administrator."
                }
            elif section == "privacy":
                return {
                    "section": "privacy", 
                    "title": "Privacy Policy",
                    "content": "Privacy Policy content will be updated by the administrator."
                }
            elif section == "hero":
                return {
                    "section": "hero",
                    "title": "Fast, Reliable, and Affordable",
                    "subtitle": "Hosting Solutions—Starting at $1/mo",
                    "description": "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions.",
                    "button_text": "Get Started Today",
                    "button_url": "https://billing.bluenebulahosting.com"
                }
            elif section == "about":
                return {
                    "section": "about",
                    "title": "About Blue Nebula Hosting",
                    "description": "Professional hosting solutions with enterprise-grade infrastructure and 24/7 support."
                }
            elif section == "features":
                return {
                    "section": "features", 
                    "title": "Why Choose Blue Nebula Hosting?",
                    "description": "We deliver enterprise-grade hosting solutions with the reliability and support your business deserves.",
                    "features": [
                        "99.9% Uptime Guarantee",
                        "24/7 Expert Technical Support", 
                        "Enterprise-Grade Security",
                        "Lightning-Fast SSD Storage",
                        "Free SSL Certificates",
                        "Daily Automated Backups",
                        "DDoS Protection",
                        "Easy One-Click Installations"
                    ]
                }
            return {"section": section, "message": "No custom content found"}
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin Content Management Endpoints
@api_router.get("/admin/content/{section}")
async def get_admin_content(section: str, current_user: str = Depends(get_current_user)):
    """Get website content by section for admin editing"""
    try:
        content = await db.website_content.find_one({"section": section})
        if not content:
            # Return default editable content structure
            default_content = {
                "section": section,
                "title": f"Default {section.title()} Title",
                "subtitle": "",
                "description": f"This is the default {section} content. Edit this in the admin panel.",
                "button_text": "Learn More",
                "button_url": "#"
            }
            if section == "features":
                default_content["features"] = [
                    "99.9% Uptime Guarantee",
                    "24/7 Expert Support",
                    "Enterprise SSD Storage"
                ]
            return default_content
        
        # Remove MongoDB _id field
        if "_id" in content:
            del content["_id"]
        
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/content/{section}")
async def create_or_update_admin_content(section: str, content_data: dict, current_user: str = Depends(get_current_user)):
    """Create or update website content by section"""
    try:
        # Add section and timestamps
        content_data["section"] = section
        content_data["updated_at"] = datetime.utcnow()
        
        # Check if content already exists
        existing = await db.website_content.find_one({"section": section})
        
        if existing:
            # Update existing content
            content_data["id"] = existing.get("id", str(uuid.uuid4()))
            result = await db.website_content.update_one(
                {"section": section},
                {"$set": content_data}
            )
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Failed to update content")
        else:
            # Create new content
            content_data["id"] = str(uuid.uuid4())
            content_data["created_at"] = datetime.utcnow()
            result = await db.website_content.insert_one(content_data)
            if not result.inserted_id:
                raise HTTPException(status_code=400, detail="Failed to create content")
        
        return {"message": f"Content for {section} saved successfully", "section": section}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/content/{section}")
async def update_admin_content(section: str, content_data: dict, current_user: str = Depends(get_current_user)):
    """Update website content by section (alternative PUT method)"""
    try:
        # Add section and timestamp
        content_data["section"] = section
        content_data["updated_at"] = datetime.utcnow()
        
        # Update or insert (upsert)
        result = await db.website_content.update_one(
            {"section": section},
            {
                "$set": content_data,
                "$setOnInsert": {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"message": f"Content for {section} updated successfully", "section": section}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/system-status")
async def get_system_status():
    """Get system status from Uptime Kuma"""
    try:
        # Make request to Uptime Kuma API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{UPTIME_KUMA_BASE_URL}/api/status-page/bnh",
                headers={"Authorization": f"Bearer {UPTIME_KUMA_API_KEY}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse the overall status
                overall_status = "operational"
                status_text = "All Systems Operational"
                
                # Check if we have incident data or status information
                if "incident" in data:
                    incidents = data.get("incident", [])
                    if incidents:
                        overall_status = "degraded"
                        status_text = "Service Issues"
                
                # Check monitor statuses if available
                if "publicGroupList" in data:
                    for group in data["publicGroupList"]:
                        for monitor in group.get("monitorList", []):
                            if monitor.get("status") == 0:  # Down
                                overall_status = "down"
                                status_text = "Service Disruption"
                                break
                            elif monitor.get("status") == 2:  # Pending
                                if overall_status == "operational":
                                    overall_status = "degraded"
                                    status_text = "Partial Outage"
                        if overall_status == "down":
                            break
                
                return {
                    "status": overall_status,
                    "text": status_text
                }
            else:
                # Fallback to checking the status page directly
                response = await client.get(f"{UPTIME_KUMA_BASE_URL}/status/bnh", timeout=10)
                if response.status_code == 200:
                    return {
                        "status": "operational",
                        "text": "All Systems Operational"
                    }
                else:
                    return {
                        "status": "unknown",
                        "text": "Status Unknown"
                    }
                    
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        return {
            "status": "unknown",
            "text": "Status Unknown"
        }

# Hardcoded hosting plans removed - using database initialization script instead

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

# Debug endpoint
@api_router.get("/debug")
async def debug():
    """Debug endpoint to check API health"""
    import os
    return {
        "status": "API Working",
        "environment": {
            "MONGO_URL": "Set" if os.environ.get('MONGO_URL') else "Not Set",
            "DB_NAME": os.environ.get('DB_NAME', 'blue_nebula_hosting'),
            "JWT_SECRET_KEY": "Set" if os.environ.get('JWT_SECRET_KEY') else "Not Set"
        },
        "timestamp": datetime.utcnow().isoformat()
    }