# Hosting Plan and Category Management Guide

## Overview

This guide covers the new hosting plan creation and category management features that have been added to fix the issues outlined in the requirements.

## Features Implemented

### 1. Database Migration Script

**File:** `backend/migrate_categories.py`

The migration script initializes the hosting categories collection with predefined categories and associates existing plans with their appropriate categories.

**Usage:**
```bash
cd backend
python migrate_categories.py
```

**Categories Created:**
- SSD Shared Hosting (`ssd_shared`)
- HDD Shared Hosting (`hdd_shared`) 
- Standard VPS (`standard_vps`)
- Performance VPS (`performance_vps`)
- Game Server Hosting (`gameserver`)
- Build Your Own Plan (`shared_byop`)
- Dockerized WordPress (`managed_wordpress`)

### 2. Backend API Endpoints

#### Create Hosting Plan
- **Endpoint:** `POST /api/admin/hosting-plans`
- **Authentication:** Required (Bearer token)
- **Description:** Creates a new hosting plan with full validation

**Request Body Example:**
```json
{
  "plan_name": "Premium SSD Plan",
  "plan_type": "ssd_shared",
  "category_key": "ssd_shared",
  "base_price": 19.99,
  "cpu_cores": 4,
  "memory_gb": 8,
  "disk_gb": 100,
  "disk_type": "SSD",
  "bandwidth": "Unlimited",
  "websites": "10",
  "email_accounts": "100",
  "subdomains": "Unlimited",
  "features": ["SSL Certificate", "Daily Backups", "24/7 Support"],
  "popular": true,
  "markup_percentage": 15,
  "docker_image": "",
  "managed_wordpress": false
}
```

#### Category Management
- **Get Categories:** `GET /api/admin/hosting-categories` (admin)
- **Create Category:** `POST /api/admin/hosting-categories` (admin)
- **Update Category:** `PUT /api/admin/hosting-categories/{id}` (admin)
- **Delete Category:** `DELETE /api/admin/hosting-categories/{id}` (admin)
- **Public Categories:** `GET /api/hosting-categories` (public)

### 3. Frontend Admin Interface

#### Plan Creation Interface

**Location:** Admin Panel > Plans Tab

**Features:**
- "Create New Plan" button in the header
- Comprehensive modal form with all plan fields
- Category selection dropdown populated from database
- Feature management (add/remove features)
- Validation for required fields
- Professional UI with proper form layout

**Required Fields:**
- Plan Name
- Category (selected from dropdown)
- Base Price (must be > 0)

**All Available Fields:**
- Basic Info: Name, Category, Price, Markup
- Resources: CPU, Memory, Disk Space, Disk Type, Bandwidth
- Shared Hosting: Websites, Email Accounts, Subdomains, Addon Domains, Databases
- Advanced: Docker Image, Managed WordPress flag
- Marketing: Popular flag, Features list

#### Category Management

**Location:** Admin Panel > Categories Tab

**Features:**
- View all categories with status and details
- Create new categories
- Edit existing categories
- Delete categories (with validation)
- Category type and sub-type management

## API Validation

### Plan Creation Validation
- Plan name uniqueness check
- Category existence validation
- Price must be positive
- Proper field type validation

### Category Validation
- Unique category key requirement
- Required fields validation
- Display order management

## Error Handling

### Backend Errors
- 400: Bad Request (validation errors, duplicate names)
- 401: Unauthorized (missing/invalid token)
- 404: Not Found (category doesn't exist)
- 500: Internal Server Error (database issues)

### Frontend Error Handling
- User-friendly error messages
- Form validation feedback
- API error display
- Loading states and user feedback

## Database Schema

### HostingCategory Collection
```javascript
{
  id: String,
  key: String,              // Unique identifier (e.g., "ssd_shared")
  display_name: String,     // Human-readable name
  description: String,      // Category description
  section_title: String,    // Title for UI sections
  section_description: String,
  type: String,            // "shared", "vps", "gameserver", "custom"
  sub_type: String,        // "ssd", "hdd", "standard", "performance", etc.
  is_active: Boolean,
  display_order: Number,
  supports_custom_features: Boolean,
  supports_containers: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### HostingPlan Collection (Extended)
```javascript
{
  id: String,
  plan_name: String,
  plan_type: String,        // Legacy field, now matches category_key
  category_key: String,     // References HostingCategory.key
  base_price: Number,
  cpu_cores: Number,
  memory_gb: Number,
  disk_gb: Number,
  disk_type: String,       // "SSD", "HDD", "NVMe"
  bandwidth: String,
  websites: String,
  email_accounts: String,
  subdomains: String,
  addon_domains: String,
  databases: String,
  features: Array,
  popular: Boolean,
  markup_percentage: Number,
  supported_games: Array,
  docker_image: String,
  managed_wordpress: Boolean,
  created_at: Date,
  updated_at: Date
}
```

## Testing

### Running Tests
```bash
cd backend
python test_plan_creation.py
```

The test script validates:
- Model instantiation and validation
- Category definitions and completeness
- Plan type to category mappings
- API endpoint registration

### Manual Testing Steps

1. **Database Migration:**
   - Run migration script
   - Verify categories are created in database
   - Check existing plans get associated with categories

2. **Category Management:**
   - Access admin panel
   - Navigate to Categories tab
   - Test create, edit, delete operations
   - Verify validation and error handling

3. **Plan Creation:**
   - Access admin panel
   - Navigate to Plans tab
   - Click "Create New Plan" button
   - Fill out form with various plan types
   - Test validation (empty fields, invalid prices)
   - Verify plans appear in appropriate categories

4. **API Testing:**
   - Test authentication requirements
   - Verify CORS handling
   - Check error responses
   - Validate data persistence

## Deployment Notes

1. **Run Migration:** Execute `migrate_categories.py` after deployment
2. **Database Backup:** Backup database before running migration
3. **Environment Variables:** Ensure MongoDB connection URL is correct
4. **Authentication:** Verify admin token functionality
5. **CORS:** Check frontend can communicate with backend

## Troubleshooting

### Common Issues

**"Error creating category: Not Found"**
- Check MongoDB connection
- Verify API routing configuration
- Confirm authentication token validity

**"Category key already exists"**
- Check for duplicate category keys
- Review migration script output
- Verify database state

**Frontend compilation errors**
- Clear node_modules and reinstall
- Check React/JavaScript syntax
- Verify all imports are correct

**Plan creation fails**
- Verify category exists in database
- Check required field validation
- Review backend logs for errors

### Debug Endpoints

- **API Health:** `GET /api/debug`
- **Available Routes:** `GET /debug/endpoints`
- **Categories:** `GET /api/hosting-categories`

## Future Enhancements

Potential improvements that could be added:

1. **Bulk Operations:** Import/export plans and categories
2. **Plan Templates:** Save common configurations as templates
3. **Advanced Validation:** Complex business rules validation
4. **Audit Trail:** Track changes to plans and categories
5. **Plan Versioning:** Maintain history of plan changes
6. **Category Icons:** Visual indicators for different category types