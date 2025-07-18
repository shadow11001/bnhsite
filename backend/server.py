from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Header, Request
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

# Debug endpoint to check what endpoints are available
@app.get("/debug/endpoints")
async def debug_endpoints():
    """Debug endpoint to show available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {"available_routes": routes}

# Create a router without prefix (Caddy will handle the /api routing)
api_router = APIRouter()

# Content management endpoints - moved to api_router for consistency
@api_router.get("/admin/content/{section}")
async def get_admin_content_direct(section: str, authorization: str = Header(None)):
    """Get website content by section for admin editing - direct endpoint"""
    try:
        # Simple auth check
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authentication required")
        
        token = authorization.split(" ")[1]
        # Basic token validation (you can enhance this)
        
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
            return default_content
        
        # Remove MongoDB _id field
        if "_id" in content:
            del content["_id"]
        
        return content
    except Exception as e:
        print(f"Error in get_admin_content_direct: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/content/{section}")
async def save_admin_content_direct(section: str, content_data: dict, authorization: str = Header(None)):
    """Save website content by section - direct endpoint"""
    try:
        # Simple auth check
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authentication required")
        
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
        print(f"Error in save_admin_content_direct: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    plan_type: str  # "ssd_shared", "hdd_shared", "custom_shared", "wordpress", "standard_vps", "performance_vps", "standard_gameserver", "performance_gameserver"
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
    # Shared hosting specific fields
    websites: Optional[str] = None  # e.g., "1", "5", "Unlimited"
    subdomains: Optional[str] = None  # e.g., "10", "Unlimited" 
    parked_domains: Optional[str] = None  # e.g., "5", "Unlimited"
    addon_domains: Optional[str] = None  # e.g., "0", "5", "Unlimited"
    databases: Optional[str] = None  # e.g., "1", "10", "Unlimited"
    email_accounts: Optional[str] = None  # e.g., "5", "Unlimited"
    # WordPress-specific fields
    container_type: Optional[str] = None  # e.g., "docker", "kubernetes"
    wp_version: Optional[str] = None  # e.g., "6.4", "latest"
    php_version: Optional[str] = None  # e.g., "8.2", "8.3"
    wp_themes: Optional[List[str]] = None  # Available WordPress themes
    wp_plugins: Optional[List[str]] = None  # Pre-installed plugins
    backup_frequency: Optional[str] = None  # e.g., "daily", "weekly", "hourly"
    ssl_management: Optional[str] = None  # e.g., "automatic", "manual"
    cdn_included: Optional[bool] = None  # Whether CDN is included
    staging_environment: Optional[bool] = None  # Whether staging is available

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
    # Shared hosting specific fields
    websites: Optional[str] = None
    subdomains: Optional[str] = None 
    parked_domains: Optional[str] = None
    addon_domains: Optional[str] = None
    databases: Optional[str] = None
    email_accounts: Optional[str] = None
    # WordPress-specific fields (public fields only)
    container_type: Optional[str] = None
    wp_version: Optional[str] = None
    php_version: Optional[str] = None
    wp_themes: Optional[List[str]] = None
    wp_plugins: Optional[List[str]] = None
    backup_frequency: Optional[str] = None
    ssl_management: Optional[str] = None
    cdn_included: Optional[bool] = None
    staging_environment: Optional[bool] = None

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
DEFAULT_ADMIN_USERNAME = "morphon"
DEFAULT_ADMIN_PASSWORD = hash_password("freemind596")  # Change this!

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

            # Ensure both 'type' and 'sub_type' are present for frontend filtering
            # If your db uses 'type' and 'sub_type', make sure to copy them to the mapped_plan
            if "type" in plan:
                mapped_plan["type"] = plan["type"]
            if "sub_type" in plan:
                mapped_plan["sub_type"] = plan["sub_type"]
            
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
        # Add timestamp to contact info
        contact_data = contact.dict()
        contact_data["timestamp"] = datetime.utcnow()
        
        # Store contact submission in database
        await db.contact_submissions.insert_one(contact_data)
        
        # Send notification email to admin
        admin_html = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>From:</strong> {contact.name} ({contact.email})</p>
        <p><strong>Subject:</strong> {contact.subject}</p>
        <p><strong>Message:</strong></p>
        <pre>{contact.message}</pre>
        """
        
        # Get admin email from company info
        company_info = await db.company_info.find_one()
        admin_email = company_info.get("contact_email") if company_info else None
        
        if admin_email:
            await send_email(
                subject=f"New Contact Form: {contact.subject}",
                message=f"New message from {contact.name} ({contact.email}):\n\n{contact.message}",
                to_email=admin_email,
                html_content=admin_html
            )
            
            # Send confirmation email to user
            user_html = f"""
            <h2>Thank you for contacting Blue Nebula Hosting</h2>
            <p>Dear {contact.name},</p>
            <p>We have received your message and will get back to you as soon as possible.</p>
            <p>Your message details:</p>
            <p><strong>Subject:</strong> {contact.subject}</p>
            <p><strong>Message:</strong></p>
            <pre>{contact.message}</pre>
            <p>Best regards,<br>Blue Nebula Hosting Team</p>
            """
            
            await send_email(
                subject="We've received your message - Blue Nebula Hosting",
                message=f"Thank you for contacting us. We have received your message and will get back to you soon.",
                to_email=contact.email,
                html_content=user_html
            )
            
        return contact_data
    except Exception as e:
        print(f"Error processing contact form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/features")
async def get_features():
    """Get hosting features and benefits"""
    return {
        "shared_hosting_features": [
            "cPanel Control Panel",
            "Free SSL Certificate",
            "Daily Backups",
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
        ],
        "custom_shared_features": [
            "Build Your Own Plan",
            "Flexible Resource Allocation",
            "Custom Configuration Options",
            "Scalable Pricing",
            "Priority Support",
            "Advanced Tools Access",
            "White Label Options"
        ],
        "wordpress_features": [
            "Managed WordPress Hosting",
            "Automatic WordPress Updates",
            "Security Hardening",
            "WordPress Expert Support",
            "Performance Optimization",
            "One-Click Staging",
            "WordPress-Specific Caching",
            "Malware Scanning & Removal",
            "Premium Theme & Plugin Library",
            "Database Optimization",
            "WordPress CLI Access",
            "Git Integration"
        ]
    }

# Update the existing /content PUT endpoint to handle legal content better
@api_router.put("/content")
async def update_content(content_update: ContentUpdate, current_user: str = Depends(get_current_user)):
    """Update website content - for admin use"""
    try:
        update_data = content_update.dict(exclude_unset=True)
        
        # Special handling for legal content
        if content_update.section in ["terms", "privacy"]:
            # Convert to legal content format
            legal_data = {
                "type": content_update.section,
                "title": update_data.get("title", ""),
                "content": update_data.get("description", ""),  # Use description as content
                "last_updated": datetime.utcnow()
            }
            
            await db.legal_content.update_one(
                {"type": content_update.section},
                {
                    "$set": legal_data,
                    "$setOnInsert": {
                        "id": str(uuid.uuid4()),
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        else:
            # Regular website content
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
        # First check website_content collection
        content = await db.website_content.find_one({"section": section})
        
        # For legal pages, also check legal_content collection if not found in website_content
        if not content and section in ["terms", "privacy"]:
            legal_content = await db.legal_content.find_one({"type": section})
            if legal_content:
                # Convert legal_content format to expected content format
                content = {
                    "section": section,
                    "title": legal_content.get("title", "Legal Document"),
                    "content": legal_content.get("content", "Content not available.")
                }
        
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
                    "description": "We deliver enterprise-grade hosting solutions with the reliability and support your business deserves."
                }
            return {"section": section, "message": "No custom content found"}
        
        # Remove MongoDB _id field for JSON serialization
        if "_id" in content:
            del content["_id"]
        
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public navigation endpoint (no authentication required)
@api_router.get("/navigation")
async def get_public_navigation():
    """Get navigation menu items for public website"""
    try:
        nav_items = await db.navigation_items.find().sort("order", 1).to_list(100)
        # Convert ObjectIds to strings and clean data
        for item in nav_items:
            if "_id" in item:
                del item["_id"]
        return nav_items
    except Exception as e:
        # Return default navigation if database fails
        return [
            {"id": "1", "label": "Home", "href": "#home", "order": 1, "is_external": False},
            {"id": "2", "label": "About", "href": "#about", "order": 2, "is_external": False},
            {"id": "3", "label": "Contact", "href": "#contact", "order": 3, "is_external": False}
        ]

# Navigation Management Endpoints
@api_router.get("/admin/navigation")
async def get_admin_navigation(current_user: str = Depends(get_current_user)):
    """Get navigation menu items - admin only"""
    try:
        nav_items = await db.navigation_items.find().sort("order", 1).to_list(100)
        # Convert ObjectIds to strings
        for item in nav_items:
            if "_id" in item:
                del item["_id"]
        return nav_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/navigation")
async def save_admin_navigation(request: Request, current_user: str = Depends(get_current_user)):
    """Save navigation menu items - admin only"""
    try:
        # Parse the JSON body manually
        navigation_data = await request.json()
        
        # Ensure it's a list
        if not isinstance(navigation_data, list):
            raise HTTPException(status_code=400, detail="Navigation data must be a list")
        
        # Clear existing navigation items
        await db.navigation_items.delete_many({})
        
        # Insert new navigation items
        for item in navigation_data:
            if "_id" in item:
                del item["_id"]
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
        
        if navigation_data:
            await db.navigation_items.insert_many(navigation_data)
        
        return {"message": "Navigation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/navigation")
async def update_admin_navigation(request: Request, current_user: str = Depends(get_current_user)):
    """Update navigation menu items - admin only (alternative PUT method)"""
    try:
        # Parse the JSON body manually
        navigation_data = await request.json()
        
        # Ensure it's a list
        if not isinstance(navigation_data, list):
            raise HTTPException(status_code=400, detail="Navigation data must be a list")
        
        # Clear existing navigation items
        await db.navigation_items.delete_many({})
        
        # Insert new navigation items
        for item in navigation_data:
            if "_id" in item:
                del item["_id"]
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
        
        if navigation_data:
            await db.navigation_items.insert_many(navigation_data)
        
        return {"message": "Navigation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SMTP Settings Management
@api_router.get("/admin/smtp-settings")
async def get_admin_smtp_settings(current_user: str = Depends(get_current_user)):
    """Get SMTP settings - admin only"""
    try:
        smtp_settings = await db.smtp_settings.find_one()
        if not smtp_settings:
            return {
                "smtp_host": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "smtp_use_tls": True,
                "from_email": "",
                "from_name": "Blue Nebula Hosting"
            }

        mapped_settings = {
            "smtp_host": smtp_settings.get("host", ""),
            "smtp_port": smtp_settings.get("port", 587),
            "smtp_username": smtp_settings.get("username", ""),
            "smtp_password": smtp_settings.get("password", ""),
            "smtp_use_tls": smtp_settings.get("use_tls", True),
            "from_email": smtp_settings.get("from_email", ""),
            "from_name": smtp_settings.get("from_name", "Blue Nebula Hosting")
        }
        
        # Remove MongoDB _id field
        if "_id" in smtp_settings:
            del smtp_settings["_id"]
        
        return smtp_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/smtp-settings")
async def update_admin_smtp_settings(smtp_data: dict, current_user: str = Depends(get_current_user)):
    """Update SMTP settings - admin only"""
    try:
        # Map frontend field names to database field names
        db_settings = {
            "host": smtp_data.get("smtp_host", ""),
            "port": smtp_data.get("smtp_port", 587),
            "username": smtp_data.get("smtp_username", ""),
            "password": smtp_data.get("smtp_password", ""),
            "use_tls": smtp_data.get("smtp_use_tls", True),
            "from_email": smtp_data.get("from_email", ""),
            "from_name": smtp_data.get("from_name", "Blue Nebula Hosting"),
            "updated_at": datetime.utcnow()
        }
        
        # Remove any _id field to avoid conflicts
        if "_id" in db_settings:
            del db_settings["_id"]
        
        # Update or insert (upsert)
        result = await db.smtp_settings.update_one(
            {},
            {
                "$set": db_settings,
                "$setOnInsert": {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"message": "SMTP settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/smtp-test")
async def test_smtp_connection(smtp_data: dict, current_user: str = Depends(get_current_user)):
    """Test SMTP connection - admin only"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        import socket
        
        # Extract SMTP settings with new field names
        host = smtp_data.get("smtp_host", "").strip()
        port = smtp_data.get("smtp_port", 587)
        username = smtp_data.get("smtp_username", "").strip()
        password = smtp_data.get("smtp_password", "").strip()
        use_tls = smtp_data.get("smtp_use_tls", True)
        
        # Validate required fields
        if not host:
            raise HTTPException(status_code=400, detail="SMTP host is required")
        if not username:
            raise HTTPException(status_code=400, detail="SMTP username is required")
        if not password:
            raise HTTPException(status_code=400, detail="SMTP password is required")
        
        # Validate port
        try:
            port = int(port)
            if port <= 0 or port > 65535:
                raise ValueError()
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid SMTP port")
        
        # Test connection with detailed error handling
        try:
            with smtplib.SMTP(host, port, timeout=10) as server:
                # Say hello to the server
                server.ehlo()
                
                # Start TLS if required
                if use_tls:
                    try:
                        server.starttls()
                        server.ehlo()  # Some servers need this again after TLS
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"TLS connection failed: {str(e)}")
                
                try:
                    server.login(username, password)
                except smtplib.SMTPAuthenticationError as e:
                    raise HTTPException(status_code=400, detail="Authentication failed: Invalid username or password")
                except smtplib.SMTPException as e:
                    raise HTTPException(status_code=400, detail=f"SMTP authentication error: {str(e)}")
                    
        except socket.gaierror as e:
            raise HTTPException(status_code=400, detail=f"Cannot connect to SMTP server: Host '{host}' not found")
        except socket.timeout as e:
            raise HTTPException(status_code=400, detail=f"Connection timeout: SMTP server '{host}:{port}' is not responding")
        except ConnectionRefusedError as e:
            raise HTTPException(status_code=400, detail=f"Connection refused: SMTP server '{host}:{port}' refused connection")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")
        
        return {"message": "SMTP connection and authentication successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during SMTP test: {str(e)}")

# Send Email Function
async def send_email(subject: str, message: str, to_email: str, html_content: Optional[str] = None):
    """Send email using configured SMTP settings"""
    try:
        # Get SMTP settings
        smtp_settings = await db.smtp_settings.find_one()
        if not smtp_settings:
            raise HTTPException(status_code=500, detail="SMTP not configured")
            
        host = smtp_settings.get("host")
        port = smtp_settings.get("port", 587)
        username = smtp_settings.get("username")
        password = smtp_settings.get("password")
        use_tls = smtp_settings.get("use_tls", True)
        from_email = smtp_settings.get("from_email")
        from_name = smtp_settings.get("from_name", "Blue Nebula Hosting")
        
        if not all([host, port, username, password, from_email]):
            raise HTTPException(status_code=500, detail="SMTP configuration incomplete")
        
        # Create the email
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Add plain text and HTML versions
        msg.attach(MIMEText(message, 'plain'))
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))
        
        # Send the email
        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.send_message(msg)
            
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Company Info Admin Endpoint (to match frontend expectations)
@api_router.get("/admin/company-info")
async def get_admin_company_info(current_user: str = Depends(get_current_user)):
    """Get company information for admin editing"""
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
        
        # Remove MongoDB _id field
        if "_id" in company:
            del company["_id"]
        
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/company-info")
async def update_admin_company_info(company_update: dict, current_user: str = Depends(get_current_user)):
    """Update company information - admin only"""
    try:
        # Add timestamp
        company_update["updated_at"] = datetime.utcnow()
        
        # Remove any _id field to avoid conflicts
        if "_id" in company_update:
            del company_update["_id"]
        
        # Update or insert (upsert)
        result = await db.company_info.update_one(
            {},
            {
                "$set": company_update,
                "$setOnInsert": {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"message": "Company info updated successfully"}
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

# Include the router in the main app with /api prefix to match Kubernetes ingress rules
app.include_router(api_router, prefix="/api")

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
